import gc
import time


class Node:
    """ Contains the order of the keys for each KeyNode.
    """

    def __init__(self, value, next=None, prev=None):
        self.limit = value
        self.next = next
        self.prev = prev


class KeyNode:
    """ Each CacheNode will contain multiple keyNodes, which will have the key.
    """

    def __init__(self, key, priority, next=None, prev=None):
        self.key = {}
        self.key[key] = Node(key)
        self.key[key].next = self.key[key]
        self.key[key].prev = self.key[key]
        self.keyAmount = 1
        self.limit = priority
        self.head = self.key[key]
        self.next = next
        self.prev = prev


class CacheNode:
    """ Create a Node that contains both priority hashedlist and expire time hashedlist.
    """

    def __init__(self, key, value, priority, expireTime, nextPriority=None, prevPriority=None, nextExpireTime=None, prevExpireTime=None):
        self.value = value
        self.priority = KeyNode(key, priority, nextPriority, prevPriority)
        self.expireTime = KeyNode(
            key, expireTime, nextExpireTime, prevExpireTime)
        self.priority.next = self.priority
        self.priority.prev = self.priority
        self.expireTime.next = self.expireTime
        self.expireTime.prev = self.expireTime


class NewCache:
    """Creating a new cache.
    """

    def __init__(self, max_items):
        self.max_items = max_items
        self.dict_of_priority = {}
        self.dict_of_expireTime = {}
        self.dict_of_keys = {}
        self.ordered = {}

    def deletePriorityKeys(self, key, dict_of_keys, index):
        """Remove priority keys from the priority linkedlist and
        hashmap.
        Time Complexity: O(1)
        """
        found = dict_of_keys[key][index]
        keyNode = found.key[key]
        if (found.keyAmount == 1):  # Only one key is in KeyNode, remove keyNode
            if found.limit == self.ordered["priority"].limit:  # head
                found.next.prev = self.ordered["priority"].prev
                self.ordered["priority"].prev.next = found.next
                self.ordered["priority"] = found.next

            elif found.limit == self.ordered["priority"].prev.limit:  # tail
                found.prev.next = self.ordered["priority"]
                self.ordered["priority"].prev = found.prev

            else:  # middle
                before = found.prev
                after = found.next
                before.next = after
                after.prev = before
            self.dict_of_priority.pop(found.limit, None)
        else:  # More than one key is in KeyNode, remove Node
            if keyNode.limit == found.head.limit:  # head
                keyNode.next.prev = found.head.prev
                found.head.prev.next = keyNode.next
                found.head = keyNode.next

            elif keyNode.limit == found.head.prev.limit:  # tail
                keyNode.prev.next = found.head
                found.head.prev = keyNode.prev

            else:  # middle
                before = keyNode.prev
                after = keyNode.next
                before.next = after
                after.prev = before
            found.keyAmount -= 1
            self.dict_of_priority[found.limit].key.pop(keyNode.limit, None)
        gc.collect()

    def deleteExpiredTimeKeys(self, key, dict_of_keys, index):
        """Remove expired time keys from the ExpireTime linkedlist and
        hashmap.
        Time Complexity: O(1)
        """
        found = dict_of_keys[key][index]
        keyNode = found.key[key]
        if (found.keyAmount == 1):
            if found.limit == self.ordered["expireTime"].limit:  # head
                found.next.prev = self.ordered["expireTime"].prev
                self.ordered["expireTime"].prev.next = found.next
                self.ordered["expireTime"] = found.next

            elif found.limit == self.ordered["expireTime"].prev.limit:  # tail
                found.prev.next = self.ordered["expireTime"]
                self.ordered["expireTime"].prev = found.prev

            else:  # middle
                before = found.prev
                after = found.next
                before.next = after
                after.prev = before
            self.dict_of_expireTime.pop(found.limit, None)
        else:
            if keyNode.limit == found.head.limit:  # head
                keyNode.next.prev = found.head.prev
                found.head.prev.next = keyNode.next
                found.head = keyNode.next

            elif keyNode.limit == found.head.prev.limit:  # tail
                keyNode.prev.next = found.head
                found.head.prev = keyNode.prev

            else:  # middle
                before = keyNode.prev
                after = keyNode.next
                before.next = after
                after.prev = before
            found.keyAmount -= 1
            self.dict_of_expireTime[found.limit].key.pop(keyNode.limit, None)
        gc.collect()

    def insertPriorityKeys(self, key, value, nodeList):
        """Inserting a priority node into the cache (ie. linkedlist + hashmap).
        Time Complexity: O(n)
        """
        searchNum = value.limit
        if not (searchNum in nodeList):  # check if priority is not in the cache
            query = self.ordered["priority"]
            if (query.limit > value.limit):  # head
                value.prev = query.prev
                query.prev.next = value
                value.next = query
                query.prev = value
                self.ordered["priority"] = value
            elif (query.prev.limit < value.limit):  # tail
                value.next = query
                value.prev = query.prev
                query.prev = value
                value.prev.next = value
            else:  # middle
                while query:
                    if (query.limit < value.limit):
                        query = query.next
                    else:
                        value.next = query
                        value.prev = query.prev
                        query.prev.next = value
                        query.prev = value
                        break
            # inserting the KeyNode into the cache
            nodeList[value.limit] = value
        else:  # if already in the cache, then add the key to the tail of the inner linkedlist + hashmap
            found = nodeList[searchNum]
            newNode = Node(key)
            lastNode = found.head.prev
            lastNode.next = newNode
            newNode.prev = lastNode
            found.head.prev = newNode
            newNode.next = found.head
            nodeList[searchNum] = found
            found.keyAmount += 1
            found.key[key] = newNode

    def insertExpireTimeKeys(self, key, value, nodeList):
        """Inserting a expire time node into the cache (ie. linkedlist + hashmap)
        Time Complexity: O(n)
        """
        searchNum = value.limit
        if not (searchNum in nodeList):
            query = self.ordered["expireTime"]
            if (query.limit > value.limit):  # head
                value.prev = query.prev
                query.prev.next = value
                value.next = query
                query.prev = value
                self.ordered["expireTime"] = value
            elif (query.prev.limit < value.limit):  # tail
                value.next = query
                value.prev = query.prev
                query.prev = value
                value.prev.next = value
            else:  # middle
                while query:
                    if (query.limit < value.limit):
                        query = query.next
                    else:
                        value.next = query
                        value.prev = query.prev
                        query.prev.next = value
                        query.prev = value
                        break
            nodeList[value.limit] = value
        else:
            found = nodeList[searchNum]
            newNode = Node(key)
            lastNode = found.head.prev
            lastNode.next = newNode
            newNode.prev = lastNode
            found.head.prev = newNode
            newNode.next = found.head
            nodeList[searchNum] = found
            found.keyAmount += 1
            found.key[key] = newNode

    def keys(self):
        """ Return all keys in the cache.
        """
        return list(self.dict_of_keys.keys())

    def evict(self):
        """ Removes the least priority node from the cache
        Time Complexity: O(1)
        """
        if self.ordered["expireTime"].limit <= time.time():  # check if the first node is expired from expire time linkedlist
            temp = self.ordered["expireTime"].head.limit
            self.deleteExpiredTimeKeys(
                self.ordered["expireTime"].head.limit, self.dict_of_keys, 1)
            self.deletePriorityKeys(temp, self.dict_of_keys, 0)
            self.dict_of_keys.pop(temp, None)

        else:
            temp = self.ordered["priority"].head.limit
            self.deletePriorityKeys(
                self.ordered["priority"].head.limit, self.dict_of_keys, 0)
            self.deleteExpiredTimeKeys(temp, self.dict_of_keys, 1)
            self.dict_of_keys.pop(temp, None)

    def set(self, key, value, priority, expireTime):
        """ Intiallizes nodes into the cache.
        TIme Complexity: O(n)
        """
        node = CacheNode(key, value, priority, expireTime)
        if (len(self.dict_of_keys) == 0) and self.max_items > 0:  # cache is empty
            node.priority.next = node.priority.prev = node.priority
            node.expireTime.next = node.expireTime.prev = node.expireTime
            self.dict_of_priority[priority] = self.ordered["priority"] = node.priority
            self.ordered["priority"] = node.priority
            self.dict_of_expireTime[expireTime] = self.ordered["expireTime"] = node.expireTime
            self.dict_of_keys[key] = {
                0: self.dict_of_priority[priority], 1: self.dict_of_expireTime[expireTime]}

        # less than max elements and key is not in the cache
        elif (len(self.dict_of_keys) < self.max_items) and (key not in self.dict_of_keys):
            self.insertPriorityKeys(key, node.priority, self.dict_of_priority)
            self.insertExpireTimeKeys(
                key, node.expireTime,  self.dict_of_expireTime)
            self.dict_of_keys[key] = {
                0: self.dict_of_priority[priority], 1: self.dict_of_expireTime[expireTime]}

        # contains max elements and key is not in the cache
        elif (len(self.dict_of_keys) >= self.max_items) and (key not in self.dict_of_keys):
            self.insertPriorityKeys(key, node.priority, self.dict_of_priority)
            self.insertExpireTimeKeys(
                key, node.expireTime,  self.dict_of_expireTime)
            self.dict_of_keys[key] = {
                0: self.dict_of_priority[priority], 1: self.dict_of_expireTime[expireTime]}
            self.evict()

        else:  # key is in the cache
            if expireTime > self.dict_of_keys[key][1].limit or priority > self.dict_of_keys[key][0].limit:
                self.deletePriorityKeys(key, self.dict_of_keys, 0)
                self.deleteExpiredTimeKeys(key, self.dict_of_keys, 1)
                self.insertPriorityKeys(key, node.priority, self.dict_of_priority)
                self.insertExpireTimeKeys(
                    key, node.expireTime,  self.dict_of_expireTime)
                self.dict_of_keys[key] = {
                    0: self.dict_of_priority[priority], 1: self.dict_of_expireTime[expireTime]}                
                
        

    def get(self, key):
        """ Place key at the bottom of the priority list when more than one
        have the same priority.
        Time Complexity: O(1)
        """
        if key in self.dict_of_keys:
            found = self.dict_of_keys[key][0]
            keyNode = found.key[key]
            if (found.head.limit == keyNode.limit):
                found.head = found.head.next
                found.key[key] = keyNode
            elif (found.head.prev.limit == keyNode.limit):
                return
            else:
                before = keyNode.prev
                after = keyNode.next
                after.prev = before
                before.next = after
                found.head.prev.next = keyNode
                keyNode.prev = found.head.prev
                keyNode.next = found.head
            self.dict_of_keys[key][0] = found

    def setMaxItems(self, max_items):
        """Set MaxItem and evict if cache has alot of nodes.
        """
        difference = self.max_items - max_items
        self.max_items = max_items
        while (difference > 0) and len(self.dict_of_keys) > 0:
            self.evict() 
            difference = difference - 1


if __name__ == "__main__":
    c = NewCache(5)
    print(time.time())
    c.set("A", 1, 1, 2000000000000000000)
    c.set("B", 1, 1, 2000000000000000000)
    c.set("D", 1, 5, 2)
    c.set("P", 1, 6, 2000000000000000000000)
    c.set("A", 1, 2, 2000000000000000000)
    c.set("L", 1, 1, 2)
    print(c.keys())
    c.get('A')
    c.setMaxItems(4)
    print(c.keys())
    c.setMaxItems(3)
    print(c.keys())
    c.setMaxItems(2)
    print(c.keys())
  

# Note: Look at this to understand how time.time() works in Python, if you want to try more examples:
# https://docs.python.org/3/library/time.html
