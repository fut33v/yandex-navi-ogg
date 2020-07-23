import re

with open('ru_optimus', 'rb') as f:
    bytes_arr = f.read()


OGGS_HEADER = "OggS".encode()
OGGS_HEADER_REGEX = re.compile(OGGS_HEADER)


def print_hex(some_bytes):
    print(''.join('{:02x} '.format(x) for x in some_bytes))


def find_ogg_in_range(start, end, fname):
    started = False
    i = 0
    for match in OGGS_HEADER_REGEX.finditer(bytes_arr, pos=start, endpos=end):
        i += 1
        oggs_index = match.span()[0]
        oggs_header = bytes_arr[oggs_index:oggs_index + 27]
        oggs_header_dict = {'version': int.from_bytes(oggs_header[4:5], 'little'),
                            'flags': int.from_bytes(oggs_header[5:6], 'little'),
                            'granule_position': oggs_header[6:14],
                            'serial_number': oggs_header[14:18],
                            'sequence_number': int.from_bytes(oggs_header[18:22], 'little'),
                            'checksum': oggs_header[22:26],
                            'total_segments': int.from_bytes(oggs_header[26:27], 'little')}
        total_segments = oggs_header_dict['total_segments']
        oggs_header = bytes_arr[oggs_index:oggs_index + 27 + total_segments]
        oggs_header_dict['segment_table'] = oggs_header[27:27+total_segments]
        print(oggs_header_dict)
        print_hex(oggs_header_dict['segment_table'])

        if oggs_header_dict['flags'] == 2:
            started = True
            start_index = match.span()[0]
        if oggs_header_dict['flags'] == 4 and started:
            started = False
            segment_table = [x for x in oggs_header_dict['segment_table']]
            segments_len = 0
            for t in segment_table:
                segments_len += t
            end_index = match.span()[0] + 27 + total_segments + segments_len

            ogg_file = bytes_arr[start_index:end_index]
            with open(fname, 'wb') as f:
                f.write(ogg_file)


file_names = []
for match in re.finditer('ru_optimus/.*?\.ogg'.encode(), bytes_arr, re.DOTALL):
    fname = match.group().decode()
    index = match.span()[1]
    file_names.append((fname, index))

print(file_names)

for i in range(0, len(file_names)):
    fname = file_names[i][0].split('/')[1]
    start = file_names[i][1]
    if i == len(file_names)-1:
        end = len(bytes_arr)
    else:
        end = file_names[i+1][1]

    find_ogg_in_range(start, end, fname)






