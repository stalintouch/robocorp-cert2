from time import sleep
from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive


@task
def order_robots_from_RobotSpareBin():
    # browser.configure(
    #     slowmo=1000,
    # )
    open_the_intranet_website()
    get_file()
    orders = get_orders()
    process_order(orders)
    archive_receipts()

def open_the_intranet_website():
    browser.goto(url='https://robotsparebinindustries.com/#/robot-order')


def get_file():
    http = HTTP()
    http.download(url='https://robotsparebinindustries.com/orders.csv', overwrite=True)

def get_orders():
    library = Tables()
    orders = library.read_table_from_csv('orders.csv', columns=['Order number', 'Head', 'Body', 'Legs', 'Address'])

    return orders

def process_order(orders):
    page = browser.page()

    for order in orders:
        fill_order(order)
        order_number = order['Order number']
        pdf_path = store_receipt_as_pdf(order_number)
        screenshot_path = take_screenshot(order_number)
        merge_screenshot_into_pdf(screenshot_path=screenshot_path, pdf_path=pdf_path)
        page.click('#order-another')

def fill_order(order):
    page = browser.page()
    page.click("button:text('OK')")
    body = str(order['Body'])
    page = browser.page()
    page.select_option('#head', order['Head'])
    page.click(f'#id-body-{body}')
    page.fill('xpath=//input[@placeholder="Enter the part number for the legs"]', order['Legs'])
    page.fill('#address', order['Address'])
    page.click('#order')

    while page.locator('.alert-danger').is_visible():
        page.click('#order')
        sleep(1)

def store_receipt_as_pdf(order_number):
    page = browser.page()
    receipt_html = page.locator('#order-completion').inner_html()
    pdf_path = f'output/receipts/receipt_{order_number}.pdf'

    pdf = PDF()
    pdf.html_to_pdf(receipt_html, pdf_path)

    return pdf_path


def take_screenshot(order_number):
    page = browser.page()
    screenshot_path = f'output/screenshots/robot_screenshot_{order_number}.png'
    page.screenshot(path=screenshot_path)

    return screenshot_path


def merge_screenshot_into_pdf(screenshot_path, pdf_path):
    pdf = PDF()
    files = [pdf_path, screenshot_path]
    pdf.add_files_to_pdf(files=files, target_document=pdf_path)


def archive_receipts():
    zip = Archive()

    zip.archive_folder_with_zip('output/receipts', 'archives.zip', recursive=True)
