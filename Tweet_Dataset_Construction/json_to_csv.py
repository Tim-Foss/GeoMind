import json
import pandas as pd

def print_headers(out_file):
    header_str = 'id,text,place_id,country_code,full_name,SW_Long,SW_Lat,NE_Long,NE_Lat,is_bbox_mid,coord_long,coor_lat\n'
    out_file.write(header_str)

def obtain_line(j_dict):
    new_line_fields = []
    #append each filed to a new line of the csv file if it exists, otherwise, append an empty string
    #seperated by a comma
    if ('id' in j_dict):
        new_line_fields.append(j_dict['id'])
    else:
        new_line_fields.append('')

    if ('text' in j_dict):
        new_line_fields.append(j_dict['text'].replace(',', '').replace('\n', ''))
    else:
        new_line_fields.append('')
    if ('geo' in j_dict):
        if ('place_id' in j_dict['geo']):
            new_line_fields.append(j_dict['geo']['place_id'])
        else:
            new_line_fields.append('')

        if ('country_code' in j_dict['geo']):
            new_line_fields.append(j_dict['geo']['country_code'])
        else:
            new_line_fields.append('')

        if ('full_name' in j_dict['geo']):
                new_line_fields.append(j_dict['geo']['full_name'].replace(',', ''))
        else:
            new_line_fields.append('')

        if ('geo' in j_dict['geo']):

            if ('bbox' in j_dict['geo']['geo']):
                for coord in (j_dict['geo']['geo']['bbox']):
                    new_line_fields.append(str(coord))
            else:
                new_line_fields.extend(['']*4)

        if ('coordinates' in j_dict['geo']):
            new_line_fields.append(str(1))
            for coord in (j_dict['geo']['coordinates']['coordinates']):
                new_line_fields.append(str(coord))
        else:
            new_line_fields.append(str(0))
            #try to find mid points and print lat and long
            try:
                sw_long, sw_lat, ne_long, ne_lat = j_dict['geo']['geo']['bbox']
            except:
                new_line_fields.extend(['']*2)
            else:
                new_line_fields.append(str((sw_long + ne_long) / 2.))
                new_line_fields.append(str((sw_lat + ne_lat) / 2.))


    return ((','.join(new_line_fields)) + '\n')


def main():
    #in_file_str should be the output file path of running Offic_Twitter_Test_Search_Tweets.py
    in_file_str = 'offic_search_tweets_test9.txt'
    #output csv file name:
    out_file_str = 'tweets_test.csv'
    with open(in_file_str, 'r') as in_file:

        json_str = in_file.read()
        json_obj = json.loads(json_str)

        with open(out_file_str, 'a+', encoding="utf-8") as out_file:

            print_headers(out_file)

            for j_dict in json_obj['data']:
                new_line = obtain_line(j_dict)
                out_file.write(new_line)



if __name__ == "__main__":
    main()