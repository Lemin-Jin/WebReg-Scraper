import scrapy


class WebregSpider(scrapy.Spider):
    name = "webreg"
    start_urls = ["file:///Users/lejin/Documents/WebReg-Scraper/testing/testing/rendered.html"]

    def parse(self, response):
        possible_line = response.css("tr")
        print(len(possible_line))

        for line in possible_line:
            header = line.css('table').css('td::text').extract()
            section_id = line.css('td[aria-describedby="search-div-b-table_SECTION_NUMBER"]::text').extract_first()
            final_label = line.css('td[aria-describedby="search-div-b-table_SECTION_NUMBER"]').css("span::text").extract_first()
            class_type = line.css('td[aria-describedby="search-div-b-table_FK_CDI_INSTR_TYPE"]::text').extract_first()
            #if (section_number != None) and (ord(section_number[0]) >= ord('0')) and (ord(section_number[0]) <= ord('9')):
            day = line.css('td[aria-describedby="search-div-b-table_DAY_CODE"]::text').extract_first()
            
            class_time = line.css('td[aria-describedby="search-div-b-table_coltime"]::text').extract_first()
            instructor = line.css('td[aria-describedby="search-div-b-table_PERSON_FULL_NAME"]::text').extract_first()
            
            if(class_time != None):
                if(class_time[0] >= '0') and (class_time <= '9'):
                    if(final_label == "FINAL"):
                        print(header, final_label, class_type, day, class_time, instructor)
                    else:
                        print(header, section_id, class_type, day, class_time, instructor)
            

        # pass
