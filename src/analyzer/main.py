#runs all trainings
# xbilyd01

import itertools
import polarity_analyzer
import class_analyzer
import aspect_analyzer


if __name__ == '__main__':
	analyzer = polarity_analyzer.Polarity_analyzer()
	analyzer = class_analyzer.Class_analyzer()
	analyzer = aspect_analyzer.Aspect_analyzer()


