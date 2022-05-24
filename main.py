from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import time
import logging


# Set up patient information here
HAPID = ''
EMAIL = ''
FIRST_NAME = ''
SURNAME = ''
DOB = ''


def monitor(target_time, female=False):
    opt = webdriver.ChromeOptions()
    opt.add_argument('headless')
    driver_location = r'C:\Users\liutu\anaconda3\chromedriver.exe'
    driver = webdriver.Chrome(driver_location, options=opt)
    driver.get('https://bmvs.onlineappointmentscheduling.net.au/oasis/')
    time.sleep(1)
    driver.find_element_by_id('ContentPlaceHolder1_btnMod').click()
    time.sleep(1)
    driver.find_element_by_id('txtHAPID').send_keys(HAPID)
    driver.find_element_by_id('txtEmail').send_keys(EMAIL)
    driver.find_element_by_id('txtFirstName').send_keys(FIRST_NAME)
    driver.find_element_by_id('txtSurname').send_keys(SURNAME)
    driver.find_element_by_id('txtDOB').send_keys(DOB)

    driver.find_element_by_id('ContentPlaceHolder1_btnSearch').click()
    time.sleep(1)
    driver.find_element_by_id('ContentPlaceHolder1_repAppointments_lnkChangeAppointment_0').click()
    time.sleep(1)

    while True:
        clinic_name = driver.find_element_by_xpath('//*[@id="dvLocationRadioGroup"]/div/table/tbody/tr/td[2]/label').text
        driver.find_element_by_id('ContentPlaceHolder1_btnCont').click()
        time.sleep(1)
        try:
            available_time = driver.find_element_by_id(
                'ContentPlaceHolder1_SelectTime1_divSearchResults').find_element_by_tag_name('h2').text
            new_available_time_obj = datetime.strptime(available_time, '%A, %d %B %Y')

            current_time = driver.find_element_by_xpath('//*[@id="form1"]/div[3]/div[2]/div/div[2]/div[1]/div[1]/div[2]').text
            current_time = current_time[:current_time.index(' @')]
            current_time_obj = datetime.strptime(current_time, '%A, %d %B %Y')

            if new_available_time_obj < current_time_obj:
                logging.info('New available time found for {} clinic: {}, trying to reschedule'.format(clinic_name, available_time))
                driver.find_element_by_id('ContentPlaceHolder1_SelectTime1_rblResults_0').click()
                driver.find_element_by_id('ContentPlaceHolder1_btnCont').click()
                time.sleep(1)
                driver.find_element_by_xpath('//*[@id="form1"]/div[3]/div[2]/div/div[2]/div[4]/button[3]').click()
                time.sleep(1)
                if female:
                    driver.find_element_by_xpath('/html/body/div[2]/button[1]').click()
                    time.sleep(1)

                time.sleep(5)
                now_time = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_divAppointmentResults"]/div/div[1]/div[1]/div[2]').text
                now_time = now_time[:now_time.index(' @')]
                now_time_obj = datetime.strptime(now_time, '%A, %d %B %Y')
                if now_time_obj == new_available_time_obj:
                    logging.info('Current time has been rescheduled to {}'.format(now_time))
                    if now_time_obj <= target_time:
                        break
                    driver.find_element_by_id('ContentPlaceHolder1_repAppointments_lnkChangeAppointment_0').click()
                    time.sleep(1)
                else:
                    logging.info('Failed to reschedule, unknown error.')
            else:
                logging.info('{} clinic has available time: {}, but not the earliest. Current scheduled time is {}'.format(clinic_name, available_time, current_time))
                driver.find_element_by_xpath('//*[@id="form1"]/div[3]/div[2]/div/div[2]/div[6]/button[2]').click()
                time.sleep(1)
        except NoSuchElementException:
            logging.info('No time available.')
            driver.refresh()
            driver.find_element_by_xpath('//*[@id="form1"]/div[3]/div[2]/div/div[2]/div[6]/button[2]').click()
            time.sleep(1)
        except:
            logging.error('Unexpected error occur! Failed to reschedule')

    driver.close()
    return False


def main():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s: %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='monitor_log.log',
                        filemode='a')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s: %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    target_time = datetime.strptime('Tuesday, 24 May 2022', '%A, %d %B %Y')
    monitor(target_time, female=True)


if __name__ == "__main__":
    main()
