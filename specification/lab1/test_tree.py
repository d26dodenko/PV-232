from tree import Tree

# tests for add, getRoot
def test_empty_tree():
	tree = Tree()
	assert tree.getRoot() is None

def test_add_root():
	tree = Tree()
	tree.add(5)
	assert tree.getRoot() is not None
	assert tree.getRoot().data == 5

def test_add_less_goes_left():
	tree = Tree()
	tree.add(5)
	tree.add(4)
	assert tree.getRoot().left.data == 4
	assert tree.getRoot().right is None

def test_add_more_goes_right():
	tree = Tree()
	tree.add(5)
	tree.add(7)
	assert tree.getRoot().right.data == 7
	assert tree.getRoot().left is None

def test_add_equal_goes_right():
	tree = Tree()
	tree.add(5)
	tree.add(5)
	assert tree.getRoot().right.data == 5
	assert tree.getRoot().left is None

def test_add_deep():
	tree = Tree()
	for i in [10, 5, 15, 20, 0]:
		tree.add(i)

	assert tree.getRoot().left.left.data == 0
	assert tree.getRoot().right.right.data == 20

# tests for find
def test_find_root():
	tree = Tree()
	tree.add(5)
	assert tree.find(5).data == 5
def test_find_left():
	tree = Tree()
	tree.add(5)
	tree.add(3)
	assert tree.find(3).data == 3

def test_find_right():
	tree = Tree()
	tree.add(5)
	tree.add(7)
	assert tree.find(7).data == 7

def test_find_missing():
	tree = Tree()
	tree.add(5)
	tree.add(7)
	assert tree.find(10) is None

def test_find_empty():
	tree = Tree()
	assert tree.find(10) is None

# test for deleteTree
def test_delete_tree():
	tree = Tree()
	tree.add(5)
	tree.add(7)
	tree.deleteTree()
	assert tree.getRoot() is None

# test for printTree
def test_print_tree(capsys):
	tree = Tree()
	for i in [10, 5, 15, 20, 0]:
		tree.add(i)
	tree.printTree()
	captured = capsys.readouterr()
	assert '0' in captured.out
	assert '5' in captured.out
	assert '10' in captured.out
	assert '15' in captured.out
	assert '20' in captured.out