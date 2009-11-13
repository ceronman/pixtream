"""
A twisted downloader
"""
from twisted.web import client
from twisted.web.client import HTTPPageDownloader, HTTPClientFactory
from twisted.internet import defer

output_file = open('fileout.out', 'wb')

class HttpStreamClient(HTTPClientFactory):
    protocol = HTTPPageDownloader

    def __init__(self, url):
        HTTPClientFactory.__init__(self, url)
        self.deferred = defer.Deferred()
        self.length = 0
        self.waiting = 1

    def pageStart(self, partialContent):
        print 'starting'
        self.waiting = 0

    def pagePart(self, data):
        self.length += len(data)
        print 'part', self.length

    def pageEnd(self):
        print 'end'
        self.deferred.callback(None)

class HTTPProgressDownloader(client.HTTPDownloader):

    def gotHeaders(self, headers):
        if self.status == '200': # page data is on the way
            if headers.has_key('content-length'):
                self.totalLength = int(headers['content-length'][0])
                print 'has length'
            else:
                self.totalLength = 0
                print 'no length'
            self.currentLength = 0.0
        return client.HTTPDownloader.gotHeaders(self, headers)

    def pagePart(self, data):
        print 'getting part'
        if self.status == '200':
            self.currentLength += len(data)
            output_file.write(data)
            if self.totalLength:
                percent = "%i%%" % (
                    (self.currentLength/self.totalLength)*100)
            else:
                percent = '%dK' % (self.currentLength/1000)
            print "Progress: " + percent

    def pageEnd(self):
        print 'End'

    def openFile(self, partialContent):
        pass

def downloadWithProgress(url, file, contextFactory=None, *args, **kwargs):

    scheme, host, port, path = client._parse(url)
    factory = HTTPProgressDownloader(url, None, *args, **kwargs)

    if scheme == 'https':
        from twisted.internet import ssl

        if contextFactory is None:
            contextFactory = ssl.ClientContextFactory( )
        reactor.connectSSL(host, port, factory, contextFactory)
    else:
        reactor.connectTCP(host, port, factory)
    return factory.deferred

def downloadWithProgress2(url):
    factory = client._makeGetterFactory(url,
                                        lambda *args: HttpStreamClient(url))

    return factory.deferred


if __name__ == "__main__":
    import sys
    from twisted.internet import reactor

    def downloadComplete(result):
        print "Download Complete."

        reactor.stop( )

    def downloadError(failure):
        print "Error:", failure.getErrorMessage( )
        reactor.stop( )

    url, outputFile = sys.argv[1:]

#    downloadWithProgress(url, outputFile).addCallback(
#        downloadComplete).addErrback(
#        downloadError)

    downloadWithProgress2(url).addCallback(
        downloadComplete).addErrback(
        downloadError)

    reactor.run()
    output_file.close()
