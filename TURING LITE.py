
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import time
import os
import json

# Function to Use the Search Box
def searchbox(tosearch):
    search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
    search_box.clear()
    search_box.send_keys(tosearch)
    time.sleep(2)
    search_box.send_keys(Keys.RETURN) # When we Press "ENTER" in the Search Box, The Group or Saved Contact Automatically Opens
    time.sleep(3)  # Wait for the search results to load completely

# Function to find the Groups Starting with the Desired Name using the Search Box
def find_groups_with_prefix(driver, prefix):
    searchbox(prefix)

    # Extract group names from search results
    group_elements = driver.find_elements("xpath", '//span[@title][@dir="auto"]')
    group_names = [group.text for group in group_elements]
    return group_names

# Function to get the Phone Number of a Person
def getphonenumber(person):
    elem_html = person.get_attribute("innerHTML")
    soup = BeautifulSoup(elem_html, 'html.parser')
    text = soup.get_text(strip=True)
    phone_number = fixstrnum(text) 
    return phone_number

# Function to remove Area Code (91)
def removeareacode(number):
    num = number - 910000000000
    return num

# Function to Fix the STR Format of Number into INT Format
def fixstrnum(strnumber):
    number = int(''.join(filter(str.isdigit, strnumber)))
    ph_num = removeareacode(number)
    return ph_num

# Function to Convert List into Set and then Set into List
def convertionoflstandset(input_list):
    mySet = set(input_list)
    output_list = list(mySet)
    return output_list

# Function to extract data from the Temp File
def extract_data_from_file(file_path):
    names = [] 
    numbers = [] 
    with open(file_path, 'r') as file:
        data = file.read()

        # Combine lines if the data is spread across multiple lines
        data = data.replace('\n', ', ')

        # Use regular expressions to find names and numbers
        name_matches = re.findall(r'[A-Za-z]+', data)
        number_matches = re.findall(r'\+91\s\d{5}\s\d{5}', data)
        
        # Add names to the names list
        names.extend(name_matches)

        # Convert and add numbers to the numbers list
        for number_str in number_matches:
            num = fixstrnum(number_str) 
            numbers.append(num)
        
    return names, numbers

driver = webdriver.Chrome()
driver.get("https://web.whatsapp.com/")
driver.maximize_window()
wait = WebDriverWait(driver, 600)

# Creating an input to temporarily stop the code until the User is ready
input("Enter any keyword after scanning QR code.\n ")

# Finding all the groups that Start with the Desired Name
prefix = "TechVerse"
all_groups = find_groups_with_prefix(driver, prefix)
time.sleep(10)
driver.refresh()
time.sleep(5)
print("All Groups: -")
print(all_groups)
time.sleep(5)
groups = [group_name for group_name in all_groups if group_name.startswith("TechVerse")]
print("\nGroups Starting with TechVerse: -")
print(groups)

with open("TempFile.txt", "w") as f:
    pass

# Traversing through all the groups
for group_name in groups:
    # WhatsApp is a little Buggy. When we Search for a group in the Search Box, we cannot use the Search Box to Search for anything else again. We have to reload the page.
    driver.refresh()
    time.sleep(5)
    print("\nAccessing Group:", group_name)
    
    # Wait
    time.sleep(2)
    
    # Opens the Group
    searchbox(group_name)

    # Wait
    time.sleep(10)
    
    # Access Group Info (Below The Group Title)
    groupinfo = '/html/body/div[1]/div/div[2]/div[4]/div/header/div[2]/div[2]/span'
    memberinfo = wait.until(EC.presence_of_element_located((By.XPATH, groupinfo)))
    text = driver.find_element(By.XPATH, groupinfo).get_attribute("title")
    print("Data Accessed!")
    
    with open("TempFile.txt", "a") as f:
        f.writelines(text)
        f.write('\n')
    
    print("\nCompleted Group:", group_name, "Moving to the Next Group.\n")
print("\nAll Groups Completed. Moving to Saved Contacts.\n")

file_path = 'TempFile.txt'
names_list, numbers_list = extract_data_from_file(file_path) 

# Creating a List of Unique Names to Avoid Repetition
unique_names_list = convertionoflstandset(names_list) 

# Finding the Phone Numbers of All the Saved Contacts
noofnames = len(unique_names_list)
print("No. of Saved Contacts in the Groups: ", noofnames)
print("Approx Time to Access 1 Contact: 20 secs")
timeforallcontacts = 20 * noofnames
print("Approx Time to Access All Contacts: ", timeforallcontacts, " secs")
for name in unique_names_list:
    # WhatsApp is a little Buggy. When we Search for a group in the Search Box, we cannot use the Search Box to Search for anything else again. We have to reload the page.
    driver.refresh()
    time.sleep(5)
    print("Accessing: ", name)
    
    # Wait
    time.sleep(2)
    
    # Opens the Group
    searchbox(name)

    # Wait
    time.sleep(10)
    
    contact_path = '/html/body/div[1]/div/div[2]/div[4]/div/header/div[2]/div/div/div/span'
    contact_element = driver.find_element("xpath", contact_path)
    contact_element.click()
    
    # Getting the Phone Number of the Member
    pnum = '/html/body/div[1]/div/div[2]/div[5]/span/div/span/div/div/section/div[1]/div[2]'
    contact_pnum = wait.until(EC.presence_of_element_located((By.XPATH, pnum)))
    num = getphonenumber(contact_pnum)
    numbers_list.append(num)
print("\nAll Tasks Completed.\nClosing WhatsApp.")
driver.quit()

# Converting List into a Set to Remove Repetitions
# We Cannot Directly dump a Set in JSON, so we will convert it back into a List
dump_list = convertionoflstandset(numbers_list)

# Creating a JSON File and Dumping all the Phone Numbers into it
with open("Phone_Numbers.json", "w") as f:
    json.dump(dump_list, f,indent = 2)

print("A JSON File Containing All the Phone Numbers has been Created.")

# Finally, We Will Delete the Temp File
file_path = 'TempFile.txt'
try:
    os.remove(file_path)
except FileNotFoundError:
    print(f"The file '{file_path}' does not exist.")
except Exception as e:
    print(f"An error occurred: {e}")
