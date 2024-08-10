import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import concurrent.futures
import queue
from tqdm import tqdm
import logging
import os
import yaml
import argparse

class GoogleScholarSearcher:
    def __init__(self, config):
        self.config = config
        self.webdriver_path = config['webdriver']['path']
        self.chrome_binary_path = config['webdriver']['chrome_binary_path']
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(filename=self.config['files']['error_log'], 
                            level=getattr(logging, self.config['logging']['level']),
                            format=self.config['logging']['format'])

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.binary_location = self.chrome_binary_path
        return webdriver.Chrome(service=Service(self.webdriver_path), options=chrome_options)

    def search_initial(self, id_value, name, organization):
        browser = self.setup_driver()
        try:
            query = f"{name} {organization if organization else ''} site:scholar.google.com"
            url = f'https://www.google.com/search?q={query.replace(" ", "+")}'
            browser.get(url)

            wait = WebDriverWait(browser, 10)
            results_div = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "dURPMd")))
            first_result = results_div.find_element(By.TAG_NAME, "div")
            first_link = first_result.find_element(By.TAG_NAME, "a")
            link_url = first_link.get_attribute("href")
            
            return id_value, name, organization, link_url
        except Exception as e:
            error_msg = f"Error searching for {name} (ID: {id_value}): {str(e)}"
            logging.error(error_msg)
            return id_value, name, organization, None
        finally:
            browser.quit()

    def search_details(self, id_new, url):
        browser = self.setup_driver()
        try:
            browser.get(url)
            wait = WebDriverWait(browser, 10)
            results_div = wait.until(EC.presence_of_element_located((By.ID, "gsc_bdy")))

            pic_div = results_div.find_element(By.ID, "gsc_prf_pu")
            profile_div = results_div.find_element(By.ID, "gsc_prf_i")
            citation_div = results_div.find_element(By.CLASS_NAME, "gsc_md_hist_b")
            
            img_link = pic_div.find_element(By.ID, "gsc_prf_pup-img").get_attribute('src') if pic_div.find_elements(By.ID, "gsc_prf_pup-img") else ''
            google_scholar_name = profile_div.find_element(By.ID, "gsc_prf_in").text if profile_div.find_elements(By.ID, "gsc_prf_in") else ''
            google_scholar_organization = profile_div.find_element(By.CLASS_NAME, "gsc_prf_il").text if profile_div.find_elements(By.CLASS_NAME, "gsc_prf_il") else ''
                
            citation_div_html = citation_div.get_attribute('outerHTML')

            try:
                soup = BeautifulSoup(citation_div_html, 'html.parser')
                years = [span.text for span in soup.find_all('span', class_='gsc_g_t')]
                citations = [span.text for span in soup.find_all('span', class_='gsc_g_al')]
                citation_data = dict(zip(years, citations))
            except:
                citation_data = {}
            return id_new, url, img_link, google_scholar_name, google_scholar_organization, citation_data
        except Exception as e:
            error_msg = f"Error searching details for {url} (ID: {id_new}): {str(e)}"
            logging.error(error_msg)
            return id_new, url, None, None, None, None
        finally:
            browser.quit()

    def search_batch(self, df, mode):
        if mode == 'initial':
            return self.search_batch_initial(df)
        elif mode == 'details':
            return self.search_batch_details(df)
        else:
            raise ValueError("Invalid search mode")

    def search_batch_initial(self, df):
        results = []
        output_file = self.config['files']['output_initial']
        
        if os.path.exists(output_file):
            existing_results = pd.read_csv(output_file)
            processed_ids = set(existing_results[self.config['columns']['id']])
            df = df[~df[self.config['columns']['id']].isin(processed_ids)]
            results = existing_results.to_dict('records')
        else:
            pd.DataFrame(columns=[self.config['columns']['id'], 'Name', 'Organization', 'Google Scholar Link']).to_csv(output_file, index=False)

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config['search']['max_workers']) as executor:
            future_to_row = {executor.submit(self.search_initial, 
                                             row[self.config['columns']['id']], 
                                             row[self.config['columns']['name']], 
                                             row.get(self.config['columns']['organization'], '')): row for _, row in df.iterrows()}
            
            with tqdm(total=len(future_to_row), desc="Searching") as pbar:
                for future in concurrent.futures.as_completed(future_to_row):
                    try:
                        id_value, name, org, link = future.result()
                        result = {
                            self.config['columns']['id']: id_value,
                            'Name': name,
                            'Organization': org if org else '',
                            'Google Scholar Link': link
                        }
                        results.append(result)
                        
                        pd.DataFrame([result]).to_csv(output_file, mode='a', header=False, index=False)
                    except Exception as e:
                        error_msg = f"Error processing a row: {str(e)}"
                        logging.error(error_msg)
                    finally:
                        pbar.update(1)
        
        return pd.DataFrame(results)

    def search_batch_details(self, df):
        results = []
        output_file = self.config['files']['output_details']
        
        if os.path.exists(output_file):
            existing_results = pd.read_csv(output_file)
            processed_ids = set(existing_results[self.config['columns']['id']])
            df = df[~df[self.config['columns']['id']].isin(processed_ids)]
            results = existing_results.to_dict('records')
        else:
            pd.DataFrame(columns=[self.config['columns']['id'], 'Google Scholar Link', 'img_link', 'google_scholar_name', 'google_scholar_organization', 'citation_data']).to_csv(output_file, index=False)

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config['search']['max_workers']) as executor:
            future_to_row = {executor.submit(self.search_details, 
                                             row[self.config['columns']['id']], 
                                             row['Google Scholar Link']): row for _, row in df.iterrows()}
            
            with tqdm(total=len(future_to_row), desc="Searching details") as pbar:
                for future in concurrent.futures.as_completed(future_to_row):
                    try:
                        _id_new, _url, _img_link, _google_scholar_name, _google_scholar_organization, _citation_data = future.result()
                        result = {
                            self.config['columns']['id']: _id_new,
                            'Google Scholar Link': _url,
                            'img_link': _img_link,
                            'google_scholar_name': _google_scholar_name,
                            'google_scholar_organization': _google_scholar_organization,
                            'citation_data': _citation_data
                        }
                        results.append(result)
                        
                        pd.DataFrame([result]).to_csv(output_file, mode='a', header=False, index=False)
                    except Exception as e:
                        error_msg = f"Error processing a row: {str(e)}"
                        logging.error(error_msg)
                    finally:
                        pbar.update(1)
        
        return pd.DataFrame(results)

def read_csv_with_encoding(file_path):
    encodings = ['utf-8', 'utf-8-sig', 'iso-8859-1', 'cp1252']
    for encoding in encodings:
        try:
            return pd.read_csv(file_path, encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Unable to read the file with any of the encodings: {encodings}")

def load_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def main():
    parser = argparse.ArgumentParser(description="Google Scholar Searcher")
    parser.add_argument('--mode', choices=['initial', 'details'], required=True,
                        help="The mode to run the script in: 'initial' for initial search or 'details' for detailed search")
    args = parser.parse_args()

    config = load_config('config.yaml')
    searcher = GoogleScholarSearcher(config)

    try:
        if args.mode == 'initial':
            df = read_csv_with_encoding(config['files']['input'])
            required_columns = [config['columns']['id'], config['columns']['name']]
        else:  # details mode
            df = read_csv_with_encoding(config['files']['output_initial'])
            required_columns = [config['columns']['id'], 'Google Scholar Link']

        print("Successfully read the CSV file.")
        print(f"Columns in the file: {df.columns.tolist()}")
        print(f"Number of rows: {len(df)}")
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        if args.mode == 'initial':
            # Handle optional organization column
            if config['columns']['organization'] not in df.columns:
                df[config['columns']['organization']] = ''
            else:
                df[config['columns']['organization']] = df[config['columns']['organization']].fillna('')

        results_df = searcher.search_batch(df, args.mode)
        print(f"Batch search completed. Results saved to '{config['files']['output_' + args.mode]}'")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        logging.error(f"Error in main function: {str(e)}")

    print(f"Error log (if any) saved to '{config['files']['error_log']}'")

if __name__ == "__main__":
    main()