#!/usr/bin/env python
# -*- coding: utf-8 -*-

class mongoParseQuery():

    __s_comp = { '$gt':'>', '$gte':'>=', '$lt':'<', '$lte':'<=', '$ne':'!=' }
    __s_logic = { '$and':'and', '$or':'or' }

    def parse_cond(self, in_cond):
        return self.__parse_cond(in_cond)

    def __parse_cond(self, in_cond):
        if isinstance(in_cond, str):
            in_cond = eval(in_cond)
        return ' '.join(self.__parse_cond_loop(in_cond))

    def __parse_cond_loop(self, in_cond):
        # print '__parse_cond_loop =', in_cond
        s_cond = []
        if isinstance(in_cond, dict) == False:
            raise ValueError('a dict type is required, but ' + in_cond.__str__())
        for k, v in in_cond.iteritems():
            if k in self.__s_logic.keys():
                s_cond.append(self.__parse_cond_logic(self.__s_logic[k], v));
            elif k in self.__s_comp.keys():
                raise ValueError('any reserved string cannot be used, ' + in_cond.__str__())
            elif isinstance(k, str):
                s_cond.append(self.__parse_cond_exp(k, v))
            else:
                raise ValueError('a logic operad or a string is required, but ' + in_cond.__str__())
        return s_cond

    def __parse_cond_exp(self, key, in_cond):
        # print '__parse_cond_exp =', in_cond
        if isinstance(in_cond, dict):
            return '%s %s' % (key, self.__parse_cond_comp(in_cond))
        elif isinstance(in_cond, list):
            s_cond = []
            for i in in_cond:
                s_cond.append('%s %s' % (key, self.__parse_cond_sentence('=', i)))
            return ' or '.join(s_cond)
        else:
            return '%s %s' % (key, self.__parse_cond_sentence('=', in_cond))

    def __parse_cond_comp(self, in_cond):
        if len(in_cond) != 1:
            raise ValueError('a single element is required, but ' + in_cond.__str__())
        k, v = in_cond.items()[0]
        if k not in self.__s_comp.keys():
            raise ValueError('invalid operand is found in ' + in_cond.__str__())
        return self.__parse_cond_sentence(self.__s_comp[k], v)

    def __parse_cond_logic(self, op, in_cond):
        # print '__parse_cond_logic =', in_cond
        s_cond = []
        if isinstance(in_cond, list) == False:
            raise ValueError('a list is required, but ' + in_cond.__str__())
        if len(in_cond) <= 1:
            raise ValueError('more than one element items are requied, but ' + in_cond.__str__())
        for i in in_cond:
            if isinstance(i, dict) == False:
                raise ValueError('the element must be a dict type, but ' + in_cond.__str__())
            s_cond.extend(self.__parse_cond_loop(i))
        return '(' + (' %s ' % op).join(s_cond) + ')'

    def __parse_cond_sentence(self, op, value):
        # print '__parse_cond_sentence =', op, ' ', value
        if isinstance(value, str) == False and isinstance(value, int) == False:
            raise ValueError('a string or integer is required, but ' + value.__str__())
        elif value in self.__s_comp.keys() or value in self.__s_logic.keys():
            raise ValueError('any reserved string cannot be used, ' + value.__str__())
        return '%s "%s"' % (op, value)

if __name__ == '__main__' :

    m = mongoParseQuery()

    print
    cond = [
        { "time": "1"},
        { "time": { "$gt" : "1" } },
        { "$and": [
            { "time": { "$gt" : "1" } },
            { "time": { "$lte": "5" } } ] },
        { "$or": [
            { "$and": [
                { "yyyy": { "$gt" : "1" } },
                { "yyyy": { "$lte": "5" } } ] },
            { "$and": [
                { "xxxx": { "$gt" : "10" } },
                { "xxxx": { "$lte": "19" } } ] } ] },
        { "time": [ "1", "2", "4" ] },
        { "$or": [
            { "time": "1"},
            { "time": "3"}, ] },
        # error case
        { "$and": { "xxx": "1", "yyy": "2" } },
        { "$or": [ { "xxx": "1" } ] },
        { "$or": [ "xxx", "1" ] },
        { "time": { "$and": "1" } },
        { "time": { "xxx" : 2 } },
        { 1: "xxx" },
        { "$gt": "1" },
        ]
    for i in cond:
        print
        print i
        try:
            m.parse_cond(i)
        except ValueError as e:
            print 'ERROR:', e
