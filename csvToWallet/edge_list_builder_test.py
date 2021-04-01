from edge_list_builder import EdgeListBuilder

#test constructor that takes the whole csv file
mappedcsv="../mapped/block600001_601667_mapped.csv"
eb=EdgeListBuilder.fromWhole(mappedcsv)
eb.constructEdgeListCSV()

#test if the resulting edgelistcsv is the same as
#constructor that filter to use the partial csv file
#mappedcsv2="../mapped/block546634_550000_mapped.csv"
#eb2=EdgeListBuilder.fromPartial(mappedcsv2,546634,547756)
#eb2.constructEdgeListCSV()

#test take a file that only contains one block
#mappedcsv3="../mapped/block546634_mapped.csv"
#eb3=EdgeListBuilder.fromWhole(mappedcsv3)
#eb3.constructEdgeListCSV()
#use ubuntu command diff to check the two files!
#appear to be the same!
