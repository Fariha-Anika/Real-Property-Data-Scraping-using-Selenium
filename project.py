"""
University of Nevada, Reno
IS 615 - Spring 2023
Final Project
project.py
Jannatul Ferdous Chadni
"""


import csv
import json
import sys
import time


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


if len(sys.argv) > 1:
    search_term = sys.argv[1]
else:
    print("Error: Expecting search term as argument 1")
    sys.exit(1)
    
num_results = None

if len(sys.argv) > 2:
    num_results = int(sys.argv[2])
    assert(num_results > 0)

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

driver = webdriver.Chrome(options=chrome_options)

url ="https://www.washoecounty.gov/assessor/cama/"
driver.get(url)

time.sleep(3)

driver.find_element(By.ID, 'saddr').click()

search_box = driver.find_element(By.ID, "search_term")

search_box.send_keys(search_term)
time.sleep(3)

search_box.send_keys(Keys.ENTER)
time.sleep(3)

xpath = '//table[@class="w3-table-all w3-hoverable"]//tr//td[2]'
apn_cells = driver.find_elements(By.XPATH, xpath)

apns = [cell.text for cell in apn_cells if cell.text != '']

apns = list(dict.fromkeys(apns))

output = {}

num_result_count = 0

for apn in apns:

    if num_results is not None:
        if num_result_count == num_results:
            break

    apn_formatted = apn

    apn = apn.replace('-', '')
    
    purl = f"{url}?parid={apn}"

    driver.get(purl)

    time.sleep(3)


    apn_data = {}


    # Owner Information
    xpath = '//th[contains(., "Situs 1")]/following-sibling::td'
    apn_data["Situs"]  = driver.find_element(By.XPATH, xpath).text.replace('\n', ' ')

    xpath = '//th[contains(., "Owner 1")]/following-sibling::td'
    apn_data["Owner"] = driver.find_element(By.XPATH, xpath).text


    # Building Information

    building_info = {}

    xpath = '//div[contains(text(), "Building Information")]/' \
            'following-sibling::table[1]/tbody/tr/th'
    keys = driver.find_elements(By.XPATH, xpath)

    bldg_keys = [k.text for k in keys]

    xpath = '//div[contains(text(), "Building Information")]/' \
            'following-sibling::table[1]/tbody/tr/td'
    values = driver.find_elements(By.XPATH, xpath)

    for key, value in zip(keys, values):
        key = key.text
        value = value.text
        
        if value:
            building_info[key] = value

    apn_data["Building Info"] = building_info
    

    # Land Information

    land_info = {}

    xpath = '//div[contains(text(), "Land Information")]/following-sibling::table[1]'
    table = driver.find_element(By.XPATH, xpath)

    xpath = "//th[contains(., 'Size')]/following-sibling::td"
    sizes = table.find_elements(By.XPATH, xpath)

    for size in sizes:
        size = size.text
        if size[-5:] == "Acres":
            break

    land_info["Size"] = size

    xpath = "//th[contains(., 'Sewer')]/following-sibling::td"
    land_info["Sewer"] = table.find_element(By.XPATH, xpath).text

    xpath = "//th[contains(., 'Street')]/following-sibling::td"
    land_info["Street"] = table.find_element(By.XPATH, xpath).text

    xpath = "//th[contains(., 'Water')]/following-sibling::td"
    land_info["Water"] = table.find_element(By.XPATH, xpath).text


    apn_data["Land Info"] = land_info

    output[apn_formatted] = apn_data

    num_result_count = num_result_count + 1
    


driver.quit()


# Save data to JSON
with open(f"washoeProperty_{search_term}.txt", "w") as outfile:
    json.dump(output, outfile, indent=4)


    
# Save data to CSV


header = ["APN", "Situs", "Owner"]

land_keys = ["Size", "Sewer", "Street", "Water"]
land_keys = ["Land_" + k for k in land_keys]


valid_bldg_keys = set()
for apn in output:
    valid_bldg_keys.update(output[apn]["Building Info"].keys())


intersection = []
for k in bldg_keys:
    if k in valid_bldg_keys:
        intersection.append(k)
bldg_keys = intersection

bldg_keys = ["Bldg_" + k for k in bldg_keys]


header = header + bldg_keys
header = header + land_keys


with open(f"washoeProperty_{search_term}_CSV.txt", "w", newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header, delimiter='|')
    writer.writeheader()

    row = {}
    for apn in output:
        row["APN"] = apn

        row["Situs"] = output[apn]["Situs"]
        row["Owner"] = output[apn]["Owner"]

        this_bldg_keys = output[apn]["Building Info"].keys()

        for k in valid_bldg_keys:
            if k in this_bldg_keys:
                row["Bldg_" + k] = output[apn]["Building Info"][k]
            else:
                row["Bldg_" + k] = ""

        for k,v in output[apn]["Land Info"].items():
            row["Land_" + k ] = v
            
            
        writer.writerow(row)



