import os
import requests
import mysql.connector
import re
import datetime
from requests.models import Response
from bs4 import BeautifulSoup
from posix import environ


DATABASE_NAME = "itjobs"
TABLE_NAME = "jobs"
US_HK_EXCHANGE_CURRENCY = 7.8


def HEADERS():
    """Return header for each request."""
    return {
        "Connection": "keep-alive",
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': 'https://www2.jobs.gov.hk/0/tc/JobSeeker/jobsearch/joblist/simple/?direct=False',
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    }


def get_session_cookies(headers):
    """Return session cookie.

    param headers: request header as a dictionary
    postcondition: correctly return website session cookies as a dictionary
    return: session cookies in a dictionary
    """
    return requests.get(
        url="https://www2.jobs.gov.hk/0/en",
        headers=headers,
        cookies={}
    )


def run_search_query(headers, session_cookies):
    """Post request to www2.jobs.gov.hk home page form for catering search.

    param headers: request header as a dictionary
    param session_cookies: website session cookies as RequestsCookieJar
    postcondition: correctly post to www2.jobs.gov.hk home page form for IT related job search
    return: requests post
    """
    return requests.post(
        url="https://www2.jobs.gov.hk/0/tc/JobSeeker/jobsearch/search/simple/",
        headers=headers,
        cookies=session_cookies,
        data={
            'criteria.jobType': 5,
            'criteria.industry': None,
            'criteria.selectedDistricts[0]': None,
            'criteria.displayMoreVac': 'true',
            'criteria.displayMoreVac': 'false',
            'criteria.salaryFr': None,
            'criteria.salaryTo': None,
            'criteria.searchField': None,
            'criteria.searchByOption': '1',
            'isMobile': 'true',
        }
    )


def connect_database():
    """Connect to MySql database."""
    return mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        user=os.environ["USER"],
        password=os.environ["PASSWORD"],
    )


def check_db_exists(mycursor):
    """Checks if databse exists, if not then create one.

    param mycursor: MySql database cursor
    postcondition: correctly checks if a database exists and if not then create a database along with a table
    """
    mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
    mycursor.execute(f"USE {DATABASE_NAME}")
    with open("jobsSchema.sql", "r") as file:
        create_table_query = file.read()
        mycursor.execute(create_table_query)


def get_index_page(page, session_cookies):
    """Retrieve www2.jobs.gov.hk index page for catering.

    param page: an integer representing the page number
    param session_cookies: website cookies as RequestCookieJar
    postcondition: correctly retrieves index page
    return: requests get
    """
    return requests.get(
        url="https://www2.jobs.gov.hk/0/en/JobSeeker/jobsearch/joblist/simple/",
        params={
            "direct": "False",
            "page": page,
        },
        cookies=session_cookies,
    )


def check_data_in_db(mycursor, order_num):
    """Check if job's order number is in database.

    param mycursor: MySql database cursor
    param order_num: a string that represents a job's order number as listed on www2.jobs.gov.hk
    postcondition: correctly returns True if order_num is in database, else False
    return: True or False boolean
    """
    mycursor.execute(
        f"SELECT * FROM {DATABASE_NAME}.{TABLE_NAME} WHERE order_num = '" + order_num + "'")
    data = mycursor.fetchall()
    return len(data) > 0


def get_pay_amount(terms):
    """Return list of pay amount.

    param terms: a string which includes salary information
    postcondition: correctly returns a list of all pay that has a $ (dollar sign)
    return: a list with pay amount as elements
    """
    match = re.findall("\$[\d]+[.]?[,]?[\d]*", terms)
    return match


def job_pay_usd_exchange(terms):
    """Convert a list of string to a list of integer that has been converted to USD.

    param terms: a string which includes wage information
    postcondition: correctly return a list of integers that has been convered to USD value
    return: a list of integers
    """
    match = get_pay_amount(terms)
    match_int = []
    for pay in match:
        new_number = ""
        for char in pay:
            if char.isnumeric():
                new_number += char
            if char == ".":
                break
        match_int.append(int(int(new_number)/US_HK_EXCHANGE_CURRENCY))
    return match_int


def job_pay_range(terms):
    """Return pay range.

    param terms: a string which includes salary information
    postcondition: correctly returns the pay range or just the base pay if the range is not provided in param terms
    return: pay range as a string
    """
    match = job_pay_usd_exchange(terms)

    if len(match) >= 2:
        return f"${match[0]} - ${match[1]}"
    else:
        return f"${match[0]}"


def check_salary_term(terms):
    """Return salary payment term.

    param terms: a string which includes salary information
    postcondition: correctly return string "per month" if salary is paid per month, else "per day"
    return: a string that is per month or per day
    """
    day = re.findall("per month", terms)

    if day:
        return "per month"
    else:
        return "per day"


def get_date_string_formatted(date):
    """Return date in format YYYY-MM-DD.

    param date: a string representing the date in the format of DD/MM/YYYY
    postcondition: correctly return date in YYYY-MM-DD format
    return: a string of formatted date as YYYY-MM-DD
    """
    org_date = datetime.datetime.strptime(date, "%d/%m/%Y")
    formatted_date = datetime.date.strftime(org_date, "%Y-%m-%d")
    return formatted_date


def get_page_data(order_num, job_link):
    """Return specific job page data as a set with string elements.

    param order_num: a string that represents a job's order number as listed on www2.jobs.gov.hk
    param job_link: a link of a specific job on www2.jobs.gov.hk
    postcondition: correctly returns the newly posted data for a job in Computer and Information Technology section on www2.jobs.gov.hk
    return: a set with thirteen string elements of the job details
    """
    response = requests.get(
        url=job_link
    )

    soup = BeautifulSoup(response.text, 'html.parser')

    get_vacant = soup.find(id="noVac")
    vacancy = str(get_vacant.text)

    get_ordNo = soup.find(id="ordNo")
    ordNo = str(get_ordNo.text)

    get_post_date = soup.find(id="postedDt")
    posted_date = str(get_post_date.text)
    create_date = get_date_string_formatted(posted_date)

    get_job_title = soup.find(id="jobTitle")
    job_title = str(get_job_title.text)

    get_emp_name = soup.find(id="empName")
    employer_name = str(get_emp_name.text)

    get_location = soup.find(id="locDesc")
    district = str(get_location.text)

    get_industry = soup.find(id="indsDesc")
    industry = str(get_industry.text)

    get_responsibility = soup.find(id="jobRemark")
    responsibility = str(get_responsibility.text)

    get_requirement = soup.find(id="eduRemark")
    requirement = str(get_requirement.text)

    get_empl_term = soup.find(id="empTerm")
    empl_term = str(get_empl_term.text)

    usd_pay_equivalent = job_pay_range(empl_term)

    salary_term = check_salary_term(empl_term)

    get_application_info = soup.find(id="openupRemark")
    application_info = str(get_application_info.text)

    get_remark = soup.find(id="propRemark")
    remark = str(get_remark.text)

    value = (job_title, usd_pay_equivalent, salary_term, str(order_num), vacancy, ordNo, create_date,  employer_name,
             district, industry, responsibility, requirement, empl_term,  application_info, remark)
    return value


def write_to_db(order_num, job_link, mycursor, mydb):
    """Write new job entry to MySql database.

    param order_num: a string that represents a job's order number as listed on www2.jobs.gov.hk
    param job_link: a link of a specific job on www2.jobs.gov.hk
    param mycursor: MySql database cursor
    param mydb: MySql database
    postcondition: correctly writes new job entry into MySql database
    """
    value = get_page_data(order_num, job_link)
    sql = "INSERT INTO jobs (job_title, usd_pay_equivalent, salary_term, order_num, vacancy, ordNo, create_date,  employer_name, district, industry, responsibility, requirement, empl_term, application_info, remark) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    mycursor.execute(sql, value)
    mydb.commit()
    print(order_num, "record inserted")


def remove_outdated_jobs(mycursor, mydb):
    """Remove rows from mysql database where createDate is more than or equal to 6 months old.

    param mycursor: MySql database cursor
    param mydb: MySql database
    postcondition: correctly delete data row in MySql database that is more than or equal to 6 months (182 days) old
    """
    sql = f"DELETE FROM {TABLE_NAME} WHERE create_date < NOW() - INTERVAL 182 DAY"
    mycursor.execute(sql)
    mydb.commit()


def main():
    headers = HEADERS()
    response = get_session_cookies(headers)
    session_cookies = response.cookies
    response = run_search_query(headers, session_cookies)
    print(f"Post state: {response.status_code}")

    mydb = connect_database()
    mycursor = mydb.cursor(buffered=True)
    check_db_exists(mycursor)

    page = 1
    while True:
        response = get_index_page(page, session_cookies)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = soup.select('div.jobseeker_grid_body > div')
        if len(jobs) == 0:
            break
        for job in jobs:
            order_num = job.find("a").contents[0]
            job_link = "https://www2.jobs.gov.hk" + job.find("a")["href"]

            if check_data_in_db(mycursor, order_num):
                break
            else:
                write_to_db(order_num, job_link, mycursor, mydb)
        page += 1
    remove_outdated_jobs(mycursor, mydb)
    print("update complete")


if __name__ == "__main__":
    main()
