import fastavro
import pprint

# Avro 파일 경로
avro_manifest_list_file = "snap-5082742676247128116-1-31e281f0-96c9-4616-a7d9-11089f81c2e4.avro"
avro_manifest_file = "31e281f0-96c9-4616-a7d9-11089f81c2e4-m0.avro"

# Avro metadata_list 파일 읽기

print('-------- avro_manifest_list_file --------')
# with open(avro_manifest_list_file, 'rb') as avro_file:
#     avro_reader = fastavro.reader(avro_file)
#     for record in avro_reader:
#         pp = pprint.PrettyPrinter(indent=2)
#         pp.pprint(record)
        

# Avro metadata_파일 읽기

# print('-------- avro_manifest_file --------')
with open(avro_manifest_file, 'rb') as avro_file:
    avro_reader = fastavro.reader(avro_file)
    for record in avro_reader:
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(record)

