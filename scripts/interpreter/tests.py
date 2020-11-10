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
    categorical = "categorical"  # test result returns category
    numerical = "numerical"     # test result returns single numerical value
    # test returns tuple, result depends on line of best fit with other data.
    bestfit = "bestfit"
    # For example it could return an (x, y, z) tuple aggregating different tests
    # to be put through least squares optimization.


allTests = []


# utilities:

def _catToNumTest(email, test, values, default):
    testResult = test(email)
    if default == None:
        assert (testResult in values), ("Unknown Category: "+str(testResult))
    if testResult in values:
        return values[testResult]
    return default

# function for turning a categorical test into a numerical test


def categoricalToNumerical(test, categoryValues: dict, defaultValue=None):
    """ Returns a callable test object equivalent to mapping category values onto numerical
        values provideded in categoryValues parameter.
        test- callable test of type categorical
        categoryValues- a dict with a key for each possible category with the numerical values
        defaultValue = None- optional parameter. Value returned for unknown category. 
                             If None enforces all categories must be in categoryValues.
    """
    assert(test.testType == TestType.categorical)
    def convertedTest(email): return _catToNumTest(
        email, test, categoryValues, defaultValue)
    convertedTest.testType = TestType.numerical
    return convertedTest


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
    readabilityFields = ["flesch_kincaid", "gunning_fog", "smog_index",
                         "automated_readability_index", "coleman_liau_index", "linsear_write"]
    return [email["readability"][field] for field in readabilityFields]
readabilityTest.testType = TestType.bestfit
readabilityTest.testName = "Agregate Readability Scores"
allTests.append(readabilityTest)

def replyToSenderTest(email):
    # if the sender is listed as the return path
    replyToSender = email["from"] in email["replyTo"]
    if replyToSender:
        return "Reply to sender"
    elif len(email["replyTo"]) > 0:
        return "Reply to other"
    return "No specified reply to"
replyToSenderTest.testType = TestType.categorical
replyToSenderTest.testName = "Reply To vs Sender"
allTests.append(replyToSenderTest)

domainCatValues = {
    "Public Domain": 1,
    "Private Domain": -1
}
_domainNum = categoricalToNumerical(domainTest, domainCatValues)

allAuthCatValues = {
    "fail": -1,
    "softfail": -0.5,
    "none": 0,
    "neutral": 0,
    "test": 0,
    "bestguesspass": 0.5,
    "pass": 1,
}
_spfNum = categoricalToNumerical(spfTest, allAuthCatValues)
_dkimNum = categoricalToNumerical(dkimTest, allAuthCatValues)
_dmarcNum = categoricalToNumerical(dmarcTest, allAuthCatValues)

replyToSenderCatValues = {
    "Reply to sender": 1,
    "No specified reply to": -1,
    "Reply to other": -1
}
_replyToSenderNum = categoricalToNumerical(replyToSenderTest, replyToSenderCatValues)

def authDomainSenderBestfit(email):
    # converts domain type, authentication results, and sender reply type into numerical values for linear fitting
    return (_domainNum(email), _spfNum(email), _dkimNum(email), _dmarcNum(email), _replyToSenderNum(email))
authDomainSenderBestfit.testType = TestType.bestfit
authDomainSenderBestfit.testName = "Domain Type and Auth Results"
allTests.append(authDomainSenderBestfit)
