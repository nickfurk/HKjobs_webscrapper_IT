CREATE TABLE IF NOT EXISTS `jobs` (
    job_title VARCHAR(255), 
    usd_pay_equivalent VARCHAR(20),
    salary_term VARCHAR(20),
    order_num VARCHAR(50), 
    vacancy VARCHAR(10), 
    ordNo VARCHAR(50), 
    create_date VARCHAR(50), 
    employer_name VARCHAR(255), 
    district VARCHAR(255), 
    industry VARCHAR(255), 
    responsibility VARCHAR(800), 
    requirement VARCHAR(800), 
    empl_term VARCHAR(800), 
    application_info VARCHAR(800), 
    remark VARCHAR(800)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
