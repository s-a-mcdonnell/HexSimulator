import solver
import sys

# To write to Excel
import xlwt 
from xlwt import Workbook 

# Information on writing to Excel here: https://www.geeksforgeeks.org/writing-excel-sheet-using-python/#
wb = Workbook()

if len(sys.argv) >= 2:
    file_name = sys.argv[1]
else:
    file_name = "Acc_states_w_mem_per_eq"


# Run solver several times with a different number of membership queries per equivalence query
# NOTE: You can set your own number of membership queries per equivalence query
'''for mem_in_eq in [20, 50, 100, 150, 200]:'''
test_num = 0
for mem_in_eq in [300, 300]:
    print(f"\nRunning test with {mem_in_eq} membership queries per equivalence query\n")
    
    try:
        solver.run_solver(mem_in_eq, show_graphs=False, accuracy_checks=True, wb=wb, test_id=test_num)
    except Exception as e:
        print(f"Error: {e}")
        wb.save(f'{file_name}.xls')
        exit(1)

    # Iterate test num
    test_num += 1

if wb:
    wb.save(f'{file_name}.xls')


