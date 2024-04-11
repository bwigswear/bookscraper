Program for finding similar books to a query book in Python.

Does the following steps:
1. Reads in book title and author as input
2. Tries to find corresponding GoodReads page
3. Searches all GoodReads lists the book is a part of to find adjacent books
4. Uses GPT API to get a similarity score of each adjacent book's synopsis to the query's synopsis
5. Using similarity score and number of similar genres, gives each book a similarity score
6. Returns the top 10 most similar books according to 0.5 * synopsis similarity + 0.5 * same genres

GPT portion of code is untested at the moment because I didn't want to pay for API credits. Would not recommend running as
it makes up to several thousand API calls on each execution. Just wanted to test basic webscraping and GPT API function calls.
If I want to continue working on this, I need to do the following things:

    1. Get OpenAI credits to test compare_books
    2. Test parse_related_lists after compare_books is done
    3. Add option to say that the query book is incorrect
    4. Add options to reduce queries made to GPT and GoodReads.com
    5. Add additional comparison vectors and a way to weight them
    6. Add a check to see if the book has a Wikipedia synopsis since those are more thorough
