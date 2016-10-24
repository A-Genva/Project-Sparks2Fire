
import urllib.request
from bs4 import  BeautifulSoup
import time


#This stores the set of all the ngos with their date_of_reg in the format name-date_of_reg
#so if there is any repetation of NGO then we can easily detect it
set_of_ngo = set()


def capitalize(string):
    '''
    Function for capitalizing the different words in the given string
    '''
    name_words = [word.capitalize() for word in string.split()]
    name = ''
    for word in name_words:
        name += word + ' '
    name = name.rstrip().replace(',',':').replace('\n', ' ')
    return name

content, soup, tr, tr_ke_bhai,siblings = [0,0,0,0,0]

def update_soup(sector, page = 0):
    '''
    Updates the soup with the sector and the page number provided
    '''
    start = time.time()
    global content, soup, tr, tr_ke_bhai,siblings
    url = "http://ngo.india.gov.in/sector_ngolist_ngo.php?page=%s&psid=%s&records=200" % (str(page), sector)
    content=urllib.request.urlopen(url).read()
    soup = BeautifulSoup(content,'lxml')
    tr = soup.find('tr', "hm_section_head_bg1")
    tr_ke_bhai = tr.find_next_siblings()
    siblings = [ele for idx, ele in enumerate(tr_ke_bhai) if idx % 2 == 0]
    stop = time.time()
    return stop-start

# All the different sectors on the internet
sectors = ['AGE', 'AGR', 'ADF', 'ZAO', 'ART', 'BIT', 'CHI',
           'CIV', 'DUP', 'DID', 'DIR', 'DWA', 'EDU', 'ENV',
           'FPR', 'HEA', 'HIV', 'HOU', 'HRT', 'ICT', 'LEM',
           'LRC', 'LAA', 'MIC', 'MSM', 'MIS', 'NRE', 'NUT',
           'PAN', 'PRI', 'RTI', 'RUR', 'SNT', 'SIR', 'SPO',
           'TUR', 'TRI', 'UDP', 'VOC', 'WAT', 'WOM', 'YOU']

file_name = 'ngo_AGE.csv'
f = open(file_name, 'w')


#Fetching the data from the base_url to the content

#This stores the pointer to the tr tag from where
# the table begins
for sector in sectors:
    #Update soup with the sector
    update_soup(sector)

    f = open('ngo_list_%s.csv' % (sector), 'w')

    #Search for the number of total items in the sector
    #on the first page and then compute the number of
    #pages based on the number of items
    pointer_to_td = soup.find('td', class_='hm_section_head_bg1')
    nums = pointer_to_td.strong.string[pointer_to_td.strong.string.find('(')+1:pointer_to_td.strong.string.find(')')]
    pages = int(nums) / 200
    print ('Number of pages to parse: ' + str(pages))

    for page in range(int(pages)+1):
        print("Page number: "+ str(page))

        #Update soup with the sector and the page number
        update_time = update_soup(sector, page)

        #If tr_ke_bhai does not have anything inside it
        if tr_ke_bhai == None:
            continue

        for bhai in siblings:
            # Name of the ngo and properly organising it
            start = time.time()
            if (bhai.a.string == None or bhai.find_all('td')[3].string == None
            or bhai.find_all('td')[4].string == None or bhai.find_all('td')[5].string == None):
                continue

            name = capitalize(bhai.a.string)


            #Getting reg_no, date_of_reg, add_of_reg of the ngo
            for idx, string in enumerate(bhai.find_all('td')[2].stripped_strings):
                if string == None:
                    continue
                if idx == 0:
                    reg_no = string[0:len(string)-12].replace(',',':').strip()
                    #First take the string then reverses the string and then slices the text between ) and (
                    #and then replace any comma with colon and then again reverses it
                    date_of_reg = string[::-1][1:11].replace(',',':')[::-1]
                else:
                    add_of_reg = capitalize(string)


            # Name of Cheif Functionary
            name_of_cheif = capitalize(bhai.find_all('td')[3].string)
            #Address of the ngo
            add_of_ngo = capitalize(bhai.find_all('td')[4].string)
            #Sectors working in
            sectors = bhai.find_all('td')[5].string.replace(',',':').replace('\n', '').strip()

            #Prints the data that is appended in a pretty format
            print('============================================================================================')
            print('|')
            print('|')
            print('|    Name: %s' %(name))
            print('|')
            print('|')
            print('|    Date of Reg: %s' % (date_of_reg))
            print('|')
            print('|')
            print('|    Reg. Number: %s' % (reg_no))
            print('|')
            print('|')
            print('|    Address of Registeration: %s' % (add_of_ngo))
            print('|')
            print('|')
            print('|    Name of Cheif: %s' % (name_of_cheif))
            print('|')
            print('|')
            print('|    Address of NGO: %s' % (add_of_ngo))
            print('|')
            print('|')
            print('|    Sectors working in : %s' % (sectors))
            print('|')
            print('|')
            print('============================================================================================')





            #If the data is not present in the set add it and append it to the file
            if name+'-'+date_of_reg not in set_of_ngo:
                set_of_ngo.add(name+'-'+date_of_reg)
                f.write('\n' + name +', '+ reg_no +', '+ date_of_reg +', '+
                add_of_reg +', '+ name_of_cheif +', '+
                add_of_ngo +', '+ sectors)

            #Printing the stats of each loop iteration
            stop = time.time()
            print("Time taken for computation of one entry: %.4f Seconds" % (stop-start))
            print('\n')
            print("Appending to %s" %(file_name))
            print('\n')
            print("Time taken for updating soup: %.2f Seconds" % (update_time))
            print('\n')

f.write('Done')
