import sys
from locator.parser import LocatorParser,OutputParser
from locator.dailydigest import DailyDigestInputParser
import logging
def main():

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s {%(pathname)s:%(lineno)d} %(message)s',
                                            datefmt='%m-%d %H:%M',
                                            )

    logger = logging.getLogger(__name__)
    logger.debug("foo")

    inputdatafile= sys.argv[1]
    with open ( inputdatafile, "rb" ) as inputdata:
        try:
            parser = LocatorParser(inputdata=inputdata,
                                inputparser=DailyDigestInputParser(),
                                outputparser=OutputParser()
                                )
            output = parser.parse()
        except Exception as e:
            logger.exception(e)
            raise e
        for outputstream in output:
            # fyi, there should normally only be one stream in our output.
            # ensure that you start from the begining of the output
            outputstream.seek(0)
            print (outputstream.read())

if __name__ == "__main__":
    main()
