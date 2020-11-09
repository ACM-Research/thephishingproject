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
    categorical = "categorical" # test result returns category
    numerical = "numerical"     # test result returns single numerical value
    bestfit = "bestfit"         # test returns tuple, result depends on line of best fit with other data.
                                # For example it could return an (x, y, z) tuple aggregating different tests
                                # to be put through least squares optimization.

allTests = []

# def testTemplate(email):
#     return ""
# testTemplate.testType = TestType.categorical
# testTemplate.testName = ""
# allTests.append(testTemplate)
def domainTest(email):
    email_services = ["hotmail", "gmail", "yahoo", "aol", "msn", "icloud"]
    m = email["from"]
    if any(email_service in m for email_service in email_services):
        return "Public Domain"
    else:
        return "Private Domain"
domainTest.testType = TestType.categorical
domainTest.testName = "Public Domain vs Private Domain"
allTests.append(domainTest)

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
dkimTest.testName = "DKIM Authentication Results"
allTests.append(dkimTest)

def dmarcTest(email):
    # map to results of email dmarc
    return email["dmarc"] or "none"
dmarcTest.testType = TestType.categorical
dmarcTest.testName = "DMARC Authentication Results"
allTests.append(dmarcTest)

def subjectivityTest(email):
    return email["sentiment"]["subjectivity"]
subjectivityTest.testType = TestType.numerical
subjectivityTest.testName = "Body Subjectivity"
allTests.append(subjectivityTest)

def readabilityTest(email):
    # aggregate test of all readability, passed through linear fitting
    readabilityFields = ["flesch_kincaid", "gunning_fog", "smog_index", "automated_readability_index", "coleman_liau_index", "linsear_write"]
    return [email["readability"][field] for field in readabilityFields]
readabilityTest.testType = TestType.bestfit
readabilityTest.testName = "Agregate Readability Scores"
allTests.append(readabilityTest)
