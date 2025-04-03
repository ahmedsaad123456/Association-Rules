import pandas as pd
from itertools import combinations
from collections import defaultdict

# Load and preprocess the dataset for the problem 2
def load_dataset_problem2(file_name, percentage):

    df = pd.read_csv(file_name, header=None, names=["Categories"] , on_bad_lines='skip')

    # Sample the dataset based on the percentage
    if 0 < percentage <= 100:
        df = df.sample(frac=percentage / 100, random_state=42)
    else:
        print("Invalid percentage! Using the full dataset.")

    # Clean the dataset
    df = df.dropna()
    
    # Create a unique transaction ID for each row
    # Using row index as unique transaction ID
    # Converts MultiIndex into regular columns
    df = df.reset_index()  
    # Assign unique transaction ID
    df["Transaction_ID"] = df.index.astype(str)  

    return df

# Create the vertical data for the problem 2
def generate_vertical_data_problem2(df, sup_count):

    vertical_data = defaultdict(set)

    
    # Populate vertical data with category → transaction mapping
    for txn_id, categories in zip(df["Transaction_ID"], df["Categories"]):
        category_list = categories.split(";")  # Split categories by semicolon
        for category in category_list:
            # Strip spaces for consistency
            vertical_data[category.strip()].add(txn_id)  


    # Filter vertical data based on support count
    filtered_vertical_data = {}
    for item, transactions in vertical_data.items():
        if len(transactions) >= sup_count:
            filtered_vertical_data[item] = transactions

    return dict(vertical_data), filtered_vertical_data



# Load and preprocess the dataset for the problem 1
def load_dataset_problem1(file_name, percentage):

    df = pd.read_csv(file_name)

    # Sample the dataset based on the percentage
    if 0 < percentage <= 100:
        df = df.sample(frac=percentage / 100, random_state=42)
    else:
        print("Invalid percentage! Using the full dataset.")

    # Clean the dataset
    df = df.dropna().drop_duplicates()
    
    # Convert 'Date' column to datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    # Create Transaction_ID with the format "Member_number_Date"
    df['Transaction_ID'] = df['Member_number'].astype(str) + "_" + df['Date'].astype(str)

    return df

# Create the vertical data for the problem 1
def generate_vertical_data_problem1(df, sup_count):

    vertical_data = defaultdict(set)

    # Create the vertical data 
    for item, txn in zip(df['itemDescription'], df['Transaction_ID']):
        vertical_data[item].add(txn)

    # Filter based on support count
    filtered_vertical_data = {}
    for item, transactions in vertical_data.items():
        if len(transactions) >= sup_count:
            filtered_vertical_data[item] = transactions

    return dict(vertical_data), filtered_vertical_data


# Generate The frequent item sets 
def generate_frequent_itemsets(filtered_vertical_data, sup_count):

    # variable to store number of combinations
        
    max_k = 2  


    # Continue generating itemsets until no more frequent sets are found
    while True:

        prev_frequent_itemsets = list(filtered_vertical_data.keys())


        # Stop if there are no more frequent itemsets
        if len(prev_frequent_itemsets) < 2:
            # print("No more frequent itemsets. Stopping.")
            break

        # Generate candidate itemsets of size max_k from previous (max_k-1) itemsets
        new_filtered_vertical_data = {}

        for a, b in combinations(prev_frequent_itemsets, 2):

            # Ensure merging happens correctly
            # Assuming `a` and `b` are two items to be merged
            if isinstance(a, tuple) and isinstance(b, tuple):
                # Merge and sort
                merged_set = sorted(set(a) | set(b))  
            else:
                # If not tuples, keep them as is
                merged_set = (a, b)  

            # convert merged_set to a tuple
            merged_set = tuple(merged_set)
            
            # Only merge sets that differ by one item
            if len(merged_set) == max_k:

                # Merge transaction sets from previous frequent itemsets
                common_transactions = filtered_vertical_data[a] & filtered_vertical_data[b]


                # Store only frequent itemsets
                if len(common_transactions) >= sup_count:
                    new_filtered_vertical_data[merged_set] = common_transactions

        # Stop if no new frequent itemsets are found
        if not new_filtered_vertical_data:
            break

        # Update for the next iteration
        filtered_vertical_data = new_filtered_vertical_data
        max_k += 1



    return filtered_vertical_data


# Function to generate all non-empty subsets of a set
def get_subsets(itemset):
    subsets = []
    for i in range(1, len(itemset)):
        subsets.extend(combinations(itemset, i))
    return subsets

# Function to calculate support for a given itemset

def calculate_support(itemset, filtered_vertical_data):
    
    # Fetch the transaction sets for each item in the combination
    transaction_sets = [filtered_vertical_data[item] for item in itemset]

    # Find the intersection of all transaction sets and return the length
    return len(set.intersection(*transaction_sets))



# Generate strong association rules

def generate_association_rules(filtered_vertical_data, one_item_vertical_data, confidence_threshold):
    rules = []

    # Iterate over all itemsets (frequent itemsets)

    for itemset, transactions in filtered_vertical_data.items():
        if len(itemset) > 1:

            # Get all non-empty subsets of the itemset
            subsets = get_subsets(itemset)

            for subset in subsets:

                # X is the subset and Y is the complement (rest of the items in the itemset)
                X = set(subset)
                Y = set(itemset) - X

                # Calculate support for X and X ∪ Y
                # For X, count how many transactions contain all items in X
                # and take the one_item vertical data 
                support_X = calculate_support(X, one_item_vertical_data)
                # Support for the entire itemset (X ∪ Y)
                support_XY = len(transactions)  
                # Calculate confidence
                confidence = support_XY / support_X if support_X > 0 else 0
                
                # If confidence is greater than or equal to the threshold, we have a strong rule
                if confidence >= confidence_threshold:
                    rules.append({
                        'Rule': f"{X} => {Y}",
                        'SupportAll': support_XY,
                        'Support': support_X,
                        'Confidence': confidence
                    })

    return rules
