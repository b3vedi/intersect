def flip_signal(wait_array):
    isRed = [False]*19
    for i in range(1, 19, 2):
        sig1 = wait_array[i]
        sig2 = wait_array[i+1]
        if sig1 < sig2:
            isRed[i] = True
        else:
            isRed[i+1] = True
    return isRed

class node:
    def __init__(self, right, left, idx):
        self.right = right
        self.left = left
        self.idx = idx

    def __init__(self) -> None:
        self.right = None
        self.left = None

def lower_bound(p, c, signal_no):
    LB = 0
    for i in range(signal_no):
        for q in range(len(p[i])):
            LB += p[i][q]
    return LB


def branching_and_bounding(root, active_nodes, isRed, c, p):
    time = lower_bound(root)
    branching(root, c, len(p[2*root.idx]), len(p[root.idx]), root.idx)
    for i in range(2, 9, 1):
        time = min(lower_bound(root.left_note), lower_bound(root.right_node))
    for i in range(active_nodes):
        if(lower_bound(i) >= time):
            active_nodes.remove(i)
            continue
        branching_and_bounding(i, active_nodes, isRed)
    time = lower_bound(active_nodes[i])
    return time


def branching(mynode, c, n1, n2, root_idx):
    temp = lower_bound(mynode)
    left_node = node(temp)
    right_node = node(temp + c[2*root_idx][2*root_idx+1])

    newnode = node(left_node, right_node)
    lower_bound(newnode)
    if(temp < n1 + n2 - 1):
        list[newnode] = max(lower_bound(newnode.left),
                            lower_bound(newnode.right))
        entireactivenode += 1
    else:
        if(max(lower_bound(newnode.left), lower_bound(newnode.right)) < temp):
            list[newnode] = max(lower_bound(newnode.left), lower_bound(newnode.right))
            entireactivenode += 1

