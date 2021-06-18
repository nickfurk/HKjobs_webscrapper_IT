# Overview

The purpose of this script is to scrape "Computer and Information Technology" jobs from www2.jobs.gov.hk while handling its sessions. Scraped data will be stored in a MySql database. Data that is over 6 months will be deleted from the database.

### Added Data

All the job's salary are converted to USD for international reference. This data can be found under the "usd_pay_equivalent" column in the MySql table.

### Content Overview

```
├─ webcrawler.py
├─ jobsSchema.sql
├─ Dockerfile
├─ README.md
```

# Requirements

1. `Docker`
2. `python 3.9`

# Link to MySql Database

In order to link to MySql database successfully, please set the environment variables for MYSQL_HOST, USER, and PASSWORD.

You can use either of the following methods:

### 1. By updating Dockerfile environment:

`ENV MYSQL_HOST="enter_host_here"`  
`ENV USER="enter_user_here"`  
`ENV PASSWORD="enter_password_here"`

OR

### 2. By command line (this overwrites the env in Dockerfile):

`export MYSQL_HOST="enter_host_here"`  
`export USER="enter_user_here"`  
`export PASSWORD="enter_password_here"`

# Docker Commands

To run an existing docker image:
`docker run scrapejobs`

To build an image:
`docker build -t [image name] .`

To run docker image:
`docker run [image name]`

# Contributor

[April Cheng](https://github.com/nickfurk)
