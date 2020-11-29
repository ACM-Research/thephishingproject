# Analyzing the Targeted Nature of Phishing Attacks

## Objective
The goal of this project is to better understand the characteristics of phishing emails sent to UTD students. It has two parts:  

### 1. Survey Study
A study was conducted in the form of a survey, in order to gain a better understanding of whether or not students are able to distinguish phishing emails from other emails.

### 2. Email Analysis
Multiple scripts were created with the goal of determining features that an automated system can use to determine whether or not an email sent to a UTD student is a phishing email. It is comprised of several components:  
1. The analyzer parses information, such as the sender, address, subject, content, and links. It also calculates readability and grammatical errors. 
2. The interpreters take this information and display it in ways that show the connection between various email features and their efficacy in classifying phishing emails from non-phishing ones. 
3. The classifier uses data gathered from the interpreters to calculate scores for each email. Using these scores, it is able to classify emails into phishing and non-phishing categories. The classifier also generates a 3-dimensional graph to better visualize results. 

## Research Poster
The below research poster details our process and results.   

![Research Poster.jpg](./poster.jpg)


## Resources

### Research Sources
 - https://www.prnewswire.com/news-releases/six-out-of-ten-americans-at-risk-of-falling-for-phishing-scam-300976988.html

### Python libraries
 - beautifulsoup4
 - language-tool-python
 - mail-parser
 - textblob
 - textstat
 - pytesseract
 - pdfminer
 - plotly
