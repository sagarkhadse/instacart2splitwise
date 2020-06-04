from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import json

def get_order_details():
    # Instacart
    driver.get('https://www.instacart.com')
    try:
        # Login
        login = driver.find_element_by_xpath('//*[@id="root"]/div/div/header/div/div[2]/div/button')
        login.click()
        email = driver.find_element_by_id('nextgen-authenticate.all.log_in_email')
        password = driver.find_element_by_id('nextgen-authenticate.all.log_in_password')
        login = driver.find_element_by_xpath('//*[@id="main-content"]/div[2]/form/div[3]/button')
        email.send_keys(config['instacart']['username'])
        password.send_keys(config['instacart']['password'])
        login.click()

        # Go to the orders page
        WebDriverWait(driver, 600).until(expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="header"]/div/div/div[1]/div[3]/div[1]/a')))
        driver.get('https://www.instacart.com/store/account/orders')
        WebDriverWait(driver, 600).until(expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="icOrdersList"]/ul/li[1]/div[1]/a')))
        latest_order_ele = driver.find_element_by_xpath('//*[@id="icOrdersList"]/ul/li[1]/div[1]/a')
        latest_order = latest_order_ele.get_attribute('href')

        # Select the latest order
        driver.get(latest_order)
        WebDriverWait(driver, 600).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'order-summary-items')))
        order_summary = driver.find_element_by_class_name('order-summary-items')
        item_list = order_summary.find_elements_by_tag_name('li')

        # Extract order items
        items = []
        subtotal = 0
        for ele in item_list:
            name = ele.find_element_by_class_name('order-status-item-details').find_element_by_tag_name('h5').text
            qty = ele.find_element_by_class_name('order-status-item-qty').find_element_by_tag_name('p').text
            cost = ele.find_element_by_class_name('order-status-item-price').find_element_by_tag_name('p').text

            if qty[-2:] == 'lb':
                qty = '1x'
            qty = int(qty[:-1])
            cost = float(cost[1:])
            if cost > 0:
                items.append({"name" : name, "qty" : qty, "cost" : cost})
                subtotal += cost

        order_totals = driver.find_element_by_class_name('order-summary-totals')
        total_rows = order_totals.find_elements_by_tag_name('tr')
        total = [row.find_elements_by_tag_name('td')[1] for row in total_rows][-2].text
        total = float(total[1:])
        tax = total - subtotal
        store = driver.find_element_by_class_name('order-summary-header-text').find_element_by_tag_name('h3').text

        order_details = {
            "store" : store,
            "items" : items,
            "subtotal" : subtotal,
            "tax" : tax,
            "total" : total
        }
        return order_details

    except Exception as e:
        print(e)

def add_splitwise_bill(order_details):

    # Splitwise
    driver.get('https://secure.splitwise.com/login')

    try:
        # Login
        form = driver.find_element_by_class_name('wrapper').find_element_by_id('new_user_session') 
        email = form.find_element_by_id('user_session_email')
        password = form.find_element_by_id('user_session_password')
        login = form.find_element_by_name('commit')
        email.send_keys(config['splitwise']['username'])
        password.send_keys(config['splitwise']['password'])
        login.click()

        # Go to the desired group
        WebDriverWait(driver, 600).until(expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="center_column"]/div[1]/div/div/a[1]')))
        driver.get('https://secure.splitwise.com/#/groups/%s' % config['splitwise']['group'])
        WebDriverWait(driver, 600).until(expected_conditions.invisibility_of_element_located((By.ID, 'loading')))

        # Add new expense
        add_btn = driver.find_element_by_xpath('//*[@id="center_column"]/div[1]/div/div/a[1]')
        add_btn.click()
        WebDriverWait(driver, 600).until(expected_conditions.visibility_of_element_located((By.ID, 'add_bill')))
        description = driver.find_element_by_xpath('//*[@id="add_bill"]/div/div[2]/div[2]/div[1]/input')
        description.send_keys(order_details['store'])
        split = driver.find_element_by_class_name('split')
        split.click()
        driver.implicitly_wait(2)

        # Choose itemized split
        WebDriverWait(driver, 600).until(expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="split_method"]/button[7]')))
        itemized_split = driver.find_element_by_xpath('//*[@id="split_method"]/button[7]')
        driver.implicitly_wait(2)
        itemized_split.click()
        WebDriverWait(driver, 600).until(expected_conditions.visibility_of_element_located((By.ID, 'item_holder')))
        item_list = driver.find_element_by_id('item_holder')

        # Add items in the list
        idx = 1
        for item in order_details['items']:
            amount = item['cost'] / item['qty']
            for count in range(item['qty']):
                item_name = driver.find_element_by_xpath('//*[@id="item_holder"]/tr[%d]/td[1]/input' % idx)
                item_amount = driver.find_element_by_xpath('//*[@id="item_holder"]/tr[%d]/td[2]/input' % idx)
                idx += 1
                item_name.send_keys(item['name'])
                item_amount.send_keys('%.2f' % amount)

        # Add tax amount
        tax = driver.find_element_by_name('tax')
        tax.send_keys('%.2f' % order_details['tax'])

        # Click done
        driver.find_element_by_xpath('//*[@id="choose_split"]/div/div/div[8]/button').click()
        WebDriverWait(driver, 600).until(expected_conditions.invisibility_of_element_located((By.ID, 'item_holder')))

        # Click save
        driver.find_element_by_xpath('//*[@id="add_bill"]/div/div[2]/footer/button[2]').click()
        WebDriverWait(driver, 600).until(expected_conditions.invisibility_of_element_located((By.ID, 'add_bill')))

    except Exception as e:
        print(type(e))
        print(e)

if __name__ == '__main__':

    with open('config.json') as json_file:
        config = json.load(json_file)

    driver = webdriver.safari.webdriver.WebDriver()
    driver.maximize_window();

    order_details = get_order_details()
    add_splitwise_bill(order_details)

    driver.close()