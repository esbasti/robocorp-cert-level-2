from robocorp.tasks import task
from robocorp import browser
from os import mkdir, path

from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
from RPA.Tables import Tables, Table
from RPA.PDF import PDF
from RPA.Archive import Archive



@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    # checking if the directory receipts exists      
    if not path.exists("output/receipts"): 
        # creating directory receipts
        mkdir("output/receipts")

    browser.configure(
        slowmo=100,
        headless=False
    )
    page = browser.page()
    open_robot_order_website()
    orders = get_orders()
    for order in orders:
        order_number = order['Order number']
        close_annoying_modal(page)
        fill_the_form(order, page)
        store_receipt_as_pdf(order_number)
        print(f"Processing order #: {order_number}")
    archive_receipts()
        

def open_robot_order_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def get_orders() -> Table:
    """Donwload Orders and read orders from Website"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    table = Tables().read_table_from_csv("orders.csv")
    return table

def close_annoying_modal(page:browser.page):
    page.click("button:text('Ok')")

def fill_the_form(order, page:browser.page):    
    order_number = str(order["Order number"])
    page.select_option("#head", str(order["Head"]))
    page.click("#id-body-"+str(order["Body"]))
    page.select_option("#head", str(order["Head"]))
    #page.fill("//html/body/div[1]/div/div[1]/div/div[1]/form/div[3]/input", str(order["Legs"]))
    page.get_by_placeholder("Enter the part number for the legs").fill(str(order["Legs"]))
    page.fill("#address ", order["Address"])
    page.click("#order")
    error_visible = page.is_visible(".alert.alert-danger")
    while error_visible:
        page.click("#order")
        error_visible = page.is_visible(".alert.alert-danger")
        print("Retrying order")
    page.screenshot(path=f"output/{order_number}.png")
    page.click("#order-another")
    

def store_receipt_as_pdf(order_number):
    pdf = PDF()
    files = [f"output/{order_number}.png"]
    pdf.add_files_to_pdf(files,f"output/receipts/{order_number}.pdf")

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "receipts.zip", recursive=True)