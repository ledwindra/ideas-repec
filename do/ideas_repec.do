********************************************************************************
* MOST DOWNLOADED AUTHOR
********************************************************************************

clear

// load data
insheet using ./data/working-paper.csv, delimiter(",")

// set variable as numeric
replace file_downloads_total = subinstr(file_downloads_total, ",", "", .)
destring file_downloads_total, replace

// keep variables
keep author file_downloads_total

// sum total downloads by author
collapse (sum) file_downloads_total, by(author)

// sort downloads and keep top 5
gsort -file_downloads_total
keep  if _n <= 5

// visualize data
graph bar (sum) file_downloads_total, ///
	over(author, sort(1)) ///
	ysize(8) ///
	xsize(20) /// 
	scheme(economist) ///
	title("Top 5 authors with most downloaded papers on RePEc") ///
	ytitle("Total downloads")

graph export ./img/author-most-downloaded.png, replace

********************************************************************************
* MOST PROLIFIC AUTHOR
********************************************************************************

clear

// load data
insheet using ./data/working-paper.csv, delimiter(",")

// count total papers by author
egen count_paper = count(working_paper), by(author)

// keep variables
keep author count_paper

// drop duplicates
duplicates drop

// sort total papers and keep top 5
gsort -count_paper
keep if _n <= 5

// visualize data
graph bar (sum) count_paper, ///
	over(author, sort(1)) ///
	ysize(8) ///
	xsize(20) /// 
	scheme(economist) ///
	title("Five most prolific economists on IDEAS/RePEc") ///
	ytitle("Total papers")

graph export ./img/prolific-economists.png, replace
