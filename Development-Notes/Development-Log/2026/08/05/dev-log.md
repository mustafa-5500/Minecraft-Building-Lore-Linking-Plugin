# 2026-08-05

Previous Entry: [2026-08-04](./2026-08-04.md)

Today we continued working on the decomposition generator, making it only show one arrow between functions, so if multiple function calls exist it does not have many of the same arrows. Also if a function returns a value the arrow is double headed, so it demonstrate data flowing to the function and coming back. Furthermore we have class based seperation, so files with multiple classes have their classes seperated helping to see the data flow of each class and how they interact.

In the future we will seperate the [Utils](../../../../Utils/) folder into a submodule so that we can pull and push updates so every project can have the same tools. It will also prevent the build up of unrelated commits for different projects.