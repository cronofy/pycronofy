class Pages(object):
    """Get paged data from Cronofy.
    Optionally iterate through all data (automatically fetching pages) or manually list and paginate.

    Example data: {'pages': {u'current': 1, u'next_page': u'https://api.cronofy.com/v1/events/pages/[blah blah]', u'total': 2},}
    """

    def __init__(self, request_handler, data, data_type, automatic_pagination=True):
        """
        :param RequestHandler request_handler: RequestHandler (for fetching subsequent pages)
        :param dict data: Dictionary containing json response from cronofy.
        :param string data_type: Type of paged data being retrieved (eg: 'events')
        :param bool automatic_pagination: Default True. During iteration automatically move to the next page.
        """
        self.request_handler = request_handler
        self.current = data['pages']['current']
        self.total = data['pages']['total']
        self.next_page_url = None
        if 'next_page' in data['pages']:
            self.next_page_url = data['pages']['next_page']
        self.data_type = data_type
        self.data = data
        self.index = 0
        self.length = len(self.data[data_type])
        self.automatic_pagination = automatic_pagination

    def all(self):
        """Return all results as a list by automatically fetching all pages.

        :return: All results.
        :rtype: ``list``
        """
        results = self.data[self.data_type]
        while self.current < self.total:
            self.fetch_next_page()
            results.extend(self.data[self.data_type])
        return results

    def current_page(self):
        """Return the current json data as a list.

        :return: Current page of data.
        :rtype: ``list``
        """
        return self.data[self.data_type]

    def fetch_next_page(self):
        """Retrieves the next page of data and refreshes Pages instance."""
        result = self.request_handler.get(url=self.next_page_url).json()
        self.__init__(self.request_handler, result,
                      self.data_type, self.automatic_pagination)

    def json(self):
        """Get the raw json data of the response
        :return: Dictionary containing response data.
        :rtype: ``dict``
        """
        return self.data

    def next(self):
        """Python 2 backwards compatibility"""
        return self.__next__()

    def __delitem__(self, idx):
        """Delete the item at idx in the returned data. Not recommended.

        :param int idx: Index
        :return: Value at index. Most likely returns a dictionary.
        :rtype: ``dict``
        """
        del self.data[self.data_type][idx]

    def __getitem__(self, idx):
        """Get the item at idx in the returned data.

        :param int idx: Index
        :return: Value at index. Most likely returns a dictionary.
        :rtype: ``dict``
        """
        return self.data[self.data_type][idx]

    def __iter__(self):
        """Function as an interator"""
        return self

    def __len__(self):
        """Get the length of the current page of data

        :return: Length of current page.
        :rtype: ``int``
        """
        return len(self.data[self.data_type])

    def __next__(self):
        """Iterate to the next item in the data set.
        By default fetch the next page if one exists.

        :return: The next item in the data set.
        :rtype: ``dict``
        """
        if self.index < self.length:
            self.index += 1
            return self.data[self.data_type][self.index - 1]
        else:
            if self.automatic_pagination and (self.current < self.total):
                self.fetch_next_page()
                return self.__next__()
            else:
                raise StopIteration()

    def __setitem__(self, idx, value):
        """Set the value of an item in the list. Not recommended.

        :param int idx: Index
        :param dict value: Value to replace the item at index with.
        """
        self.data[self.data_type][idx] = value
