import os
import glob

def visit_all_years(basedir) :
	for file_name in glob.iglob(basedir + "\\*", recursive=False) :
		print(file_name)
		visit_single_year(file_name)

def visit_single_year(dirname) :
	year = dirname.split("\\")[-1]
	for file_name in glob.iglob(dirname + "\\" + year + "-???", recursive=False) :
		old_file = file_name.split("\\")[-1]
		suffix = old_file.split("-")[-1]
		new_file = suffix + "-" + year
		print('\t', dirname + "\\" + old_file + " --> " + dirname + "\\" + new_file)
		os.rename(dirname + "\\" + old_file, dirname + "\\" + new_file)
		
month_map = {
	"01" : "Jan",
	"02" : "Feb",
	"03" : "Mar",
	"04" : "Apr",
	"05" : "May",
	"06" : "Jun",
	"07" : "Jul",
	"08" : "Aug",
	"09" : "Sep",
	"10" : "Oct",
	"11" : "Nov",
	"12" : "Dec"
}

visit_all_years("C:\\Users\\Jhumnu\\Pictures\\PicturesByMonths")
