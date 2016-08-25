from simple_tree import Node
import compare



A = (
    Node("a")
        .addkid(Node("b")
            .addkid(Node("c")
            	.addkid(Node("d")
                	.addkid(Node("m1"))
                	.addkid(Node("m2")))))
        .addkid(Node("e")
        	.addkid(Node("x")
        		.addkid(Node("m3")))
        	.addkid(Node("y")
        		.addkid(Node("m4"))))
    )
B1 = (
    Node("a")
        .addkid(Node("b")
        	.addkid(Node("d")
        		.addkid(Node("m3"))
        		.addkid(Node("m4"))))
        .addkid(Node("e1")
        	.addkid(Node("x1")
        		.addkid(Node("m1")))
        	.addkid(Node("y1")
        		.addkid(Node("m2"))))
    )

B2 = (
    Node("a")
        .addkid(Node("e1")
        	.addkid(Node("x1")
        		.addkid(Node("m1")))
        	.addkid(Node("y1")
        		.addkid(Node("m2"))))
        .addkid(Node("b")
        	.addkid(Node("d")
        		.addkid(Node("m3"))
        		.addkid(Node("m4"))))
    )


dist = compare.simple_distance(A, B2, Node.get_children)
print dist






