import json, requests, sys
import argparse

#
# # Helper functions
#

# Format a Jenkins REST API URL
def makeurl(repo, buildid, query=''):
    headurl='https://jenkins.esss.dk/dm/job/ess-dmsc/job/'
    tailurl='api/json?pretty=true'
    return '{}/{}/job/master/{}/{}/{}'.format(headurl, repo, buildid, query, tailurl)


# Do HTTP request and return as json
def getjsonfromurl(url):
    result=requests.get(url)
    return json.loads(result.text)


# Get json field by name at top level
def getjson(repo, metric, url, stats):
    data = getjsonfromurl(url)
    res = []
    for stat in stats:
        value = data[stat]
        res.append("ci.{}.{}.{} {}".format(repo, metric, stat, value))
    return res

# Get json fields by name from the action list
def getjsonfields(url, field):
    data = getjsonfromurl(url)
    try:
        for action in data['actions']:
            if action['_class'] == field:
                return action
    except:
        return ''
    return ''


# build times can be in any offset in the actions array
# so we search through it
def gettimes(repo, metric, url, stats):
    data = getjsonfields(url, 'jenkins.metrics.impl.TimeInQueueAction')
    if (data == ''):
        return ''

    res = []
    for stat in stats:
        value = data[stat]
        res.append("ci.{}.{}.{}  {}".format(repo, metric, stat, value))
    return res


# Returns the build data in seconds
def getdatesec(repo, url):
    data = getjsonfromurl(url)
    return int(data['timestamp']/1000)

#
# # Main functionality below
#

def getmetrics(repo, buildid):
    datesecs = getdatesec(repo, makeurl(repo, buildid))

    metrics = []

    url = makeurl(repo, buildid)
    metrics += gettimes(repo, 'buildtimes', url, ['buildingDurationMillis', 'executingTimeMillis'])

    for query in queries:
        url = makeurl(repo, buildid, query[1])
        metrics += getjson(repo, query[0], url, query[2])

    for metric in metrics:
        print("echo '{} {}' | nc 172.30.242.21 2003".format(metric, datesecs))



# Queries that return metrics that are reported at top level and which
# requires no array searches
queries = [
            ['test',     'testReport',      ['passCount', 'failCount', 'skipCount']],
            ['sloc',     'sloccountResult', ['totalFiles', 'totalLines']],
            ['cppcheck', 'cppcheck', ['totalSize', 'newSize']]
        ]

#ids = [637, 636]
#for id in range(619, 637 + 1):
#    print("# {}".format(id))
#    getmetrics('event-formation-unit', id)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", metavar='repo', help = "repository",
                       type = str, default = "event-formation-unit")
    parser.add_argument("-b", metavar='buildid', help = "Jenkins build id",
                       type = int, required = True)
    args = parser.parse_args()

    print("{}, {}".format(args.r, args.b))

    getmetrics(args.r, args.b)
