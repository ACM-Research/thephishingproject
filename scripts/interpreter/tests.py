""" Module containing multiple tests that run on a single email.

Tests are functions but (here's a little bit of bad practice for you) have values assigned to them
indicating what type of test they are / what their graph should display:
    test.testType = 
        TestType.categorical - returns data in categories
        TestType.numerical - returns data as a numerical value

Tests are also given names for the purpose of graphing. These can be any strings.
    test.testName = "testname"
"""
class TestType:
    categorical = "categorical"
    numerical = "numerical"

allTests = []

# def testTemplate(email):
#     return ""
# testTemplate.testType = TestType.categorical
# testTemplate.testName = ""
# allTests.append(testTemplate)

def spfTest(email):
    # map to results of email spf
    return email["spf"] or "none"
spfTest.testType = TestType.categorical
spfTest.testName = "SPF Authentication Results"
allTests.append(spfTest)

def dkimTest(email):
    # map to results of email dkim
    return email["dkim"] or "none"
dkimTest.testType = TestType.categorical
spfTest.testName = "DKIM Authentication Results"
allTests.append(dkimTest)

def dmarcTest(email):
    # map to results of email dmarc
    return email["dmarc"] or "none"
dmarcTest.testType = TestType.categorical
spfTest.testName = "DMARC Authentication Results"
allTests.append(dmarcTest)
