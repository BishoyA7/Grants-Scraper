import time
import json 
from bs4 import BeautifulSoup
from langchain_community.document_loaders import BSHTMLLoader
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By 
from selenium.webdriver.support import expected_conditions as EC

# URL of the page with the HTML content
url = 'https://www.grants.gov/search-grants/'

# Initialize pages variable
pages = 5 

# List to store all grants
all_grants = []

for page in range(1, pages):
    # Initialize the Selenium WebDriver 
    driver = webdriver.Chrome()

    # Open the URL in the browser
    driver.get(url)

    # Allow some time for the page to load 
    time.sleep(5)

    # Get the page source after it has loaded
    page_source = driver.page_source

    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find all 'tr' elements with a specific attribute
    div_element = soup.find('div', class_ ='usa-table-container--scrollable')
    tbody_element = div_element.find('tbody')
    # tbody_element.append(div_element.find('tfoot'))
    # print(tbody_element)

    if page != 1: 
        # Use WebDriverWait to wait for the next button to be clickable
        next_page = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//nav/ul/li[{page}]/a"))
        )
        next_page.click()

        # Wait for the page to load after clicking the next button
        time.sleep(5)

        # Get the updated page source
        page_source = driver.page_source

        # Parse the HTML content with BeautifulSoup
        soup_new = BeautifulSoup(page_source, 'html.parser')
        div_element = soup_new.find('div', class_='usa-table-container--scrollable')
        tbody_element = div_element.find('tbody')


    # Iterate through each 'tr' element
    for target_tr in tbody_element:
        # Extract specific attributes from the 'td' elements within the 'tr'
        grant_title = target_tr.find('td', tabindex='0').find_next('td').text
        agency = target_tr.find('td', tabindex='0').find_next('td').find_next('td').text
        status = target_tr.find('td', tabindex='0').find_next('td').find_next('td').find_next('td').text
        start_date = target_tr.find('td', tabindex='0').find_next('td').find_next('td').find_next('td').find_next('td').text
        end_date = target_tr.find('td', tabindex='0').find_next('td').find_next('td').find_next('td').find_next('td').find_next('td').text

        # Extract link from the 'td' element
        link = target_tr.find('td', tabindex='0').find('a')['href']
        
        # Open the link in a new tab and switch to it
        driver.execute_script(f"window.open('{link}', '_blank')")
        driver.switch_to.window(driver.window_handles[-1])

        #Allow some time for the page to load
        time.sleep(5)

        # Get the HTML content of the new page
        new_page_source = driver.page_source

        # Parse the HTML content of the new page with BeautifulSoup
        new_page_soup = BeautifulSoup(new_page_source, 'html.parser')
        # print(new_page_soup)

        general_info_div = new_page_soup.find('div', class_ = 'flex-6')
        funding_category = general_info_div.find('td', string = "Category of Funding Activity:").find_next('td').text

        general_info_div2 = new_page_soup.find('div', class_ = 'flex-6').find_next('div', class_ = 'flex-6')
        program_funding = general_info_div2.find('td', string = "Estimated Total Program Funding:").find_next('td').text
        award_ceiling = general_info_div2.find('td', string = "Award Ceiling:").find_next('td').text

        eligibility_div = new_page_soup.find('div', class_ = 'display-flex flex-row flex-align-stretch')
        eligible_applicants = eligibility_div.find('td', string = "Eligible Applicants:").find_next('td').text
        eligible_info = eligibility_div.find('td', string = "Additional Information on Eligibility:").find_next('td').text 

        eligibility_div2 = new_page_soup.find('div', class_ = 'display-flex flex-row flex-align-stretch').find_next('div', class_ = 'display-flex flex-row flex-align-stretch')
        description = eligibility_div2.find('td', string = "Description:").find_next('td').text

        # Find the 'a' tag within the 'td' tag containing "Link to Additional Information:"
        link_td = eligibility_div2.find('td', string="Link to Additional Information:").find_next('td')
        link_a = link_td.find('a')

        # Check if the 'a' tag is found and has an 'href' attribute
        if link_a and 'href' in link_a.attrs:
            grant_link = link_a['href']
        else:
            grant_link = "NA"
        
        #Check if status is forecasted to fill in End Date
        if status == "Forecasted":
            end_date = "TBD"

        # Organize the extracted information into a dictionary
        grant_info = {
            "Grant Title": grant_title,
            "Agency": agency,
            "Status": status,
            "Start Date": start_date,
            "End Date": end_date,
            "Category of Funding Activity": funding_category,
            "Estimated Total Program Funding": program_funding,
            "Award Ceiling": award_ceiling,
            "Eligible Applicants": eligible_applicants,
            "Additional Information on Eligibility": eligible_info,
            "Description:": description,
            "Link to Additional Information": grant_link
        }

        all_grants.append(grant_info)
        
    # Append the dictionary to the list of all grants
    driver.quit()

# Save the list of grants to a JSON file  
json_file = 'grants_data.json'
with open(json_file, 'w', encoding='utf-8') as json_file:
    json.dump(all_grants, json_file, ensure_ascii=False, indent=4)

print(f"Grant information has been saved to '{json_file}'.")