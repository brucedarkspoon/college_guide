# College Search Guide Streamlit App 

## Overview 
This is a Streamlit Application based on College Mobility Data and College Scorecard.
This app allows users to explore colleges in the United States.
It allows you to filter colleges by various criteria and visualize the results.
Specifically, it allows you to:
* ***Filter*** section allows users to filter colleges based on user-specific criteria, such as Barron’s selectivity index, average SAT score, or tuitions and fees. It shows information about colleges that match to the filtering criteria such as the number of matching colleges, the location of each college, size of college, etc.
* ***View*** section provides more detailed information on individual colleges. Users can type the name of their college of interest to search quickly. Detailed information on the selected college such as SAT scores, tuitions, and median income of graduates are displayed through graphs.    
* ***Compare*** section provides visual comparisons between selected colleges. Much like the View section, it provides information about colleges through graphs, but the information about the selected colleges are overlaid on top of each other.

## Overview of the College Mobility Data
* This data track the income of students and their parents focusing on ***1980-1982 birth cohorts***
* Parental income is obtained based on the income of the parents at the time of the student's admission to college.
* Child income is obtained based on the income of the student ~10 years after graduation.
* Mobility rate is the fraction of students who move from the bottom 20% of parental income to the top 20% (or 1%) of child income.
* When year is not specified, it usually refers to the cohort of early 2000s.
* Please visit [Opportunity Insights Web Page](https://opportunityinsights.org/paper/mobilityreportcards/) for more information

## Overview of the College Scorecard Data
* Institution-level data files for 1996-97 through 2020-21 containing aggregate data for each institution. 
* It includes information on institutional characteristics, enrollment, student aid, costs, and student outcomes.
* Please visit [College Scorecard Web Page](https://collegescorecard.ed.gov/) for more information

## How to Access the College Search Guide App

### Visit the Online App

If you want to use this app without any modification, you can simply visit the
[College Search Guide App](https://college-guide.streamlit.app/) hosted by [streamlit.io](https://streamlit.io/)

### Clone and run the app locally

If you want to clone this repository and run on your computer (possibly with modifications), you can follow the instruction below.

```
## you need git installed on your computer
git clone https://github.com/brucedarkspoon/college_guide.git  

cd college_guide

## you need python3 installed on your computer
pip3 install pandas streamlit pydeck 

streamlit run app.py
```
