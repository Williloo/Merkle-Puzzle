# Merkle Puzzle

# Theory
## Actions
Client Side initiates the Merkle Puzzle to generate a unique key for server
and client to communicate from this point forwards.

### Client Action:
Generates a number of 'secrets' to send to the server. Each 'secret' is made
up of:

__B1 + H1 + B2__

-  B1: Random 16 bytes
-  H1: Hash of x concatenations of B1
-  B2: Random 16 bytes 

### Server Action:
1. Solve the puzzle - pick a random 'secret' and start cracking the hash until
you get x.
2. Send back to the server H2, the hash of B1 concatenated x times.

### Client Action:
Match the hash received H2 to pre-calculated hashes of x*B2's, and get the index x.

From this point onwards: BOTH SIDES USE X*B2 AS ENCRYPTION KEY.


## Justification
If an adversary had access to all communications, they have access to:
1. All the 'secrets'
2. H2

Can they use this information to beat the O(N*M) time asymetry? 
- No way to get information about secrets without cracking secrets...no crossover effect
- As generating from all English words, no list to start off with, except generating
  hashes for large concatenations of random words
- If wanted to crack by iterating x concats of W2's...still have to try all of them indefinitely to match hash

# TODO
-  Change nonce between every message, encoding the current nonce with the previous cipher