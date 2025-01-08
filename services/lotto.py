from sqlalchemy.orm import Session
from model.table import WinningNumber
from schema.lotto import WinningNumberCreate
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import logging
from collections import Counter
logging.basicConfig(level=logging.DEBUG)
async def create_winning_number(db: Session, request: WinningNumberCreate):
    new_number = WinningNumber(numbers=request.numbers, date=request.date)
    await db.add(new_number)
    await db.commit()
    await db.refresh(new_number)
    return new_number

async def get_all_winning_numbers(db: Session):
    return await db.query(WinningNumber).all()

async def scrape_numbers(db: Session, lottoname):
    try:
       
        all_numbers = []
        
        for year in range(2010, 2025):
            response = requests.get(f"https://ca.lottonumbers.com/{lottoname}/numbers/{str(year)}")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            rows = soup.find_all("tr")
            for idx ,row in enumerate(rows, 1):
                    # Locate the <td> with class balls-row
                balls_row = row.select_one("td.balls-row")
                if not balls_row :
                    continue  # Skip rows without a balls-row

                # Extract normal balls from <ul> inside balls-row
                normal_balls = [li.text for li in balls_row.select("ul > li.ball.ball")][:7]
                # Extract bonus ball from <ul> inside balls-row
                bonus_ball = balls_row.select_one("ul > li.ball.bonus-ball").text if balls_row.select_one("ul > li.ball.bonus-ball") else None
                
                # Extract date column
                date_row = row.select_one("td.date-row")
                date_text = date_row.select_one("br").find_next_sibling(text=True).strip()
                def mergeNum(normal_balls):
                    for numbers in enumerate(normal_balls, 1):
                        return ' '.join(str(number) for number in normal_balls)
                #Extract Jackpot
                if lottoname == "lotto-max":
                    jackpot_row = row.select_one("td.stat-row").get_text(strip=True).split("$")[1]
                    
                    
                    date_object = datetime.strptime(date_text, "%B %d %Y")
                    # Format it as YYYY-MM-DD
                    formatted_date = date_object.strftime("%Y-%m-%d")

                    # Append to the list
                    all_numbers.append({
                        "date": formatted_date,
                        "winningNumbers": normal_balls,
                        "bonus ball": bonus_ball if bonus_ball else None,
                        "jackpot": f"${jackpot_row}",
                    })
                else:
                    date_object = datetime.strptime(date_text, "%B %d %Y")
                    # Format it as YYYY-MM-DD
                    formatted_date = date_object.strftime("%Y-%m-%d")

                    # Append to the list
                    all_numbers.append({
                        "date": formatted_date,
                        "winningNumbers": normal_balls,
                        "bonus ball": bonus_ball if bonus_ball else None,
                    })

        df = pd.DataFrame(all_numbers)

        # Step 4: Track occurrences of all numbers (1-99) for each day
        all_numbers_occurred = {str(i): [] for i in range(1, 100)}  # Create a dictionary to hold counts for each number

        # Step 4a: Loop through each row and count occurrences of each number
        for index, row in df.iterrows():
            winning_numbers = row['winningNumbers']
            for number in range(1, 100):
                # Check if the number is in the winning numbers for this draw
                if str(number) in winning_numbers:
                    all_numbers_occurred[str(number)].append(row['date'])

        # Step 5: Create a frequency table of occurrences
        number_frequency_by_day = {}
        for number, dates in all_numbers_occurred.items():
            # Count occurrences of the number for each day
            day_count = pd.Series(dates).value_counts().to_dict()
            number_frequency_by_day[number] = day_count

        # Step 6: Find the most frequent number for each day
        most_frequent_number_by_day = {}

        for date in df['date'].unique():
            max_frequency = 0
            most_frequent_number = None
            for number, day_counts in number_frequency_by_day.items():
                count = day_counts.get(date, 0)
                if count > max_frequency:
                    max_frequency = count
                    most_frequent_number = number
            most_frequent_number_by_day[date] = most_frequent_number

        # Step 7: Add comments to the Excel sheet for the most frequent number of each day
        df['comments'] = df['date'].apply(lambda x: f"Most frequent number: {most_frequent_number_by_day.get(x, 'N/A')}" if x in most_frequent_number_by_day else "")

        # Step 8: Save the data with comments to an Excel file
        excel_file = f"{lottoname}_winning_numbers.xlsx"
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Lotto Results', index=False)
            worksheet = writer.sheets['Lotto Results']

            # Add comments to the Excel cells for the most frequent number of each day
            for row_idx, date in enumerate(df['date']):
                if df.at[row_idx, 'comments']:
                    worksheet.write_comment(f'F{row_idx+2}', df.at[row_idx, 'comments'])  # Assuming 'comments' in column 'F'

        # Output the result to the console
        print(f"Most frequent numbers have been tracked and saved to '{excel_file}'.")
        return excel_file
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"status": "error", "message": str(e)}, 500
    
# lottomax
async def scrape_and_get_frequency(db: Session, lottoname):
    try:
        all_numbers = []
        for year in range(2010, 2025):
            response = requests.get(f"https://ca.lottonumbers.com/{lottoname}/numbers/{str(year)}")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            rows = soup.find_all("tr")
            for idx ,row in enumerate(rows, 1):
                # Locate the <td> with class balls-row
                balls_row = row.select_one("td.balls-row")
                if not balls_row :
                    continue  # Skip rows without a balls-row
      
                # Extract normal balls from <ul> inside balls-row
                normal_balls = [li.text for li in balls_row.select("ul > li.ball.ball")][:7]

                # Extract bonus ball from <ul> inside balls-row
                bonus_ball = balls_row.select_one("ul > li.ball.bonus-ball").text if balls_row.select_one("ul > li.ball.bonus-ball") else None
                
                # Extract date column
                date_row = row.select_one("td.date-row")
                date_text = date_row.select_one("br").find_next_sibling(text=True).strip()

               
                def mergeNum(normal_balls):
                    for numbers in enumerate(normal_balls, 1):
                        return ' '.join(str(number) for number in normal_balls)
                
                date_object = datetime.strptime(date_text, "%B %d %Y")
                # Format it as YYYY-MM-DD
                formatted_date = date_object.strftime("%Y-%m-%d")

                # Append to the list
                all_numbers.append({
                    "Date": formatted_date,
                    "WinningNumbers": normal_balls,
                    "bonus ball": bonus_ball if bonus_ball else None,
                })
        
        df = pd.DataFrame(all_numbers)
        
        df['Date'] = pd.to_datetime(df['Date'])

        # Extract the month and year for grouping
        df['Month'] = df['Date'].dt.to_period('M')

        # Function to find the most frequent numbers
        def top_frequent(numbers_list, top_n=4):
            # Flatten the list of lists
            flat_list = [num for sublist in numbers_list for num in sublist]
            # Count occurrences
            freq_counter = Counter(flat_list)
            # Get the top_n most common numbers
            most_common = freq_counter.most_common(top_n)
            # Pad with (None, 0) if less than top_n numbers
            most_common += [(None, 0)] * (top_n - len(most_common))
            # Return only numbers and their frequencies
            return most_common

        # Group by Month and calculate the top frequent numbers for each month
        result = df.groupby('Month')['WinningNumbers'].apply(lambda x: top_frequent(x, top_n=4)).reset_index()
        # sort values by month
        result =  result.sort_values(by='Month', ascending=False)
        # Split the results into separate columns for each rank
        for i in range(4):  # Adjust range for the desired top_n numbers
            result[f'MostFrequentNumber_{i+1}'] = result['WinningNumbers'].apply(lambda x: x[i][0])
            result[f'Frequency_{i+1}'] = result['WinningNumbers'].apply(lambda x: x[i][1])

        # Drop the original WinningNumbers column
        result.drop(columns='WinningNumbers', inplace=True)

        print(result)

        # Export to Excel
        with pd.ExcelWriter(f"{lottoname}_Most_Frequent_Numbers.xlsx") as writer:
            result.to_excel(writer, index=False, sheet_name="Frequency by Month")

        return f"{lottoname}_Most_Frequent_Numbers.xlsx"
        
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return e

async def scrape_ontario_numbers(db: Session):
    try:
       
        all_numbers = []
        
        for year in range(2010, 2025):
            response = requests.get(f"https://ca.lottonumbers.com/ontario/ontario-49/numbers/{str(year)}")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            rows = soup.find_all("tr")
            for idx ,row in enumerate(rows, 1):
                    # Locate the <td> with class balls-row
                balls_row = row.select_one("td.balls-row")
                if not balls_row :
                    continue  # Skip rows without a balls-row

                # Extract normal balls from <ul> inside balls-row
                normal_balls = [li.text for li in balls_row.select("ul > li.ball.ball")][:7]
                # Extract bonus ball from <ul> inside balls-row
                bonus_ball = balls_row.select_one("ul > li.ball.bonus-ball").text if balls_row.select_one("ul > li.ball.bonus-ball") else None
                
                # Extract date column
                date_row = row.select_one("td.date-row")
                date_text = date_row.select_one("br").find_next_sibling(text=True).strip()

                #Extract Encore
                encore_row = row.select_one('td[data-title="Encore Numbers"]')
                encore_numbers = [li.text for li in encore_row.select("ul.balls > li.ball")]
                
                def mergeNum(normal_balls):
                    for num in enumerate(normal_balls, 1):
                        return ' '.join(str(num) for num in normal_balls)
                
                date_object = datetime.strptime(date_text, "%B %d %Y")
                # Format it as YYYY-MM-DD
                formatted_date = date_object.strftime("%Y-%m-%d")

                # Append to the list
                all_numbers.append({
                    "date": formatted_date,
                    "winningNumbers": normal_balls,
                    "bonus ball": bonus_ball if bonus_ball else None,
                    "encore numbers" : mergeNum(encore_numbers)
                })
        df = pd.DataFrame(all_numbers)
        # Step 4: Track occurrences of all numbers (1-99) for each day
        all_numbers_occurred = {str(i): [] for i in range(1, 100)}  # Create a dictionary to hold counts for each number

        # Step 4a: Loop through each row and count occurrences of each number
        for index, row in df.iterrows():
            winning_numbers = row['winningNumbers']
            for number in range(1, 100):
                # Check if the number is in the winning numbers for this draw
                if str(number) in winning_numbers:
                    all_numbers_occurred[str(number)].append(row['date'])

        # Step 5: Create a frequency table of occurrences
        number_frequency_by_day = {}
        for number, dates in all_numbers_occurred.items():
            # Count occurrences of the number for each day
            day_count = pd.Series(dates).value_counts().to_dict()
            number_frequency_by_day[number] = day_count

        # Step 6: Find the most frequent number for each day
        most_frequent_number_by_day = {}

        for date in df['date'].unique():
            max_frequency = 0
            most_frequent_number = None
            for number, day_counts in number_frequency_by_day.items():
                count = day_counts.get(date, 0)
                if count > max_frequency:
                    max_frequency = count
                    most_frequent_number = number
            most_frequent_number_by_day[date] = most_frequent_number

        # Step 7: Add comments to the Excel sheet for the most frequent number of each day
        df['comments'] = df['date'].apply(lambda x: f"Most frequent number: {most_frequent_number_by_day.get(x, 'N/A')}" if x in most_frequent_number_by_day else "")
        today = datetime.today()
        # Step 8: Save the data with comments to an Excel file
        excel_file = f'ontario49_winning_results.xlsx'
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Lotto Results', index=False)
            worksheet = writer.sheets['Lotto Results']

            # Add comments to the Excel cells for the most frequent number of each day
            for row_idx, date in enumerate(df['date']):
                if df.at[row_idx, 'comments']:
                    worksheet.write_comment(f'F{row_idx+2}', df.at[row_idx, 'comments'])  # Assuming 'comments' in column 'F'

        # Output the result to the console
        print(f"Most frequent numbers have been tracked and saved to '{excel_file}'.")
        return excel_file
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"status": "error", "message": str(e)}, 500
    

async def scrape_and_get_ontario49_frequency(db: Session):
    try:
        all_numbers = []
        for year in range(2010, 2025):
            response = requests.get(f"https://ca.lottonumbers.com/ontario/ontario-49/numbers/{str(year)}")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            rows = soup.find_all("tr")
            for idx ,row in enumerate(rows, 1):
                # Locate the <td> with class balls-row
                balls_row = row.select_one("td.balls-row")
                if not balls_row :
                    continue  # Skip rows without a balls-row
      
                # Extract normal balls from <ul> inside balls-row
                normal_balls = [li.text for li in balls_row.select("ul > li.ball.ball")][:7]

                # Extract bonus ball from <ul> inside balls-row
                bonus_ball = balls_row.select_one("ul > li.ball.bonus-ball").text if balls_row.select_one("ul > li.ball.bonus-ball") else None
                
                # Extract date column
                date_row = row.select_one("td.date-row")
                date_text = date_row.select_one("br").find_next_sibling(text=True).strip()

               
                def mergeNum(normal_balls):
                    for numbers in enumerate(normal_balls, 1):
                        return ' '.join(str(number) for number in normal_balls)
                
                date_object = datetime.strptime(date_text, "%B %d %Y")
                # Format it as YYYY-MM-DD
                formatted_date = date_object.strftime("%Y-%m-%d")

                # Append to the list
                all_numbers.append({
                    "Date": formatted_date,
                    "WinningNumbers": normal_balls,
                    "bonus ball": bonus_ball if bonus_ball else None,
                })
        
        df = pd.DataFrame(all_numbers)
        
        df['Date'] = pd.to_datetime(df['Date'])

        # Extract the month and year for grouping
        df['Month'] = df['Date'].dt.to_period('M')

        # Function to find the most frequent numbers
        def top_frequent(numbers_list, top_n=4):
            # Flatten the list of lists
            flat_list = [num for sublist in numbers_list for num in sublist]
            # Count occurrences
            freq_counter = Counter(flat_list)
            # Get the top_n most common numbers
            most_common = freq_counter.most_common(top_n)
            # Pad with (None, 0) if less than top_n numbers
            most_common += [(None, 0)] * (top_n - len(most_common))
            # Return only numbers and their frequencies
            return most_common

        # Group by Month and calculate the top frequent numbers for each month
        result = df.groupby('Month')['WinningNumbers'].apply(lambda x: top_frequent(x, top_n=4)).reset_index()
        # sort values by month
        result =  result.sort_values(by='Month', ascending=False)
        # Split the results into separate columns for each rank
        for i in range(4):  # Adjust range for the desired top_n numbers
            result[f'MostFrequentNumber_{i+1}'] = result['WinningNumbers'].apply(lambda x: x[i][0])
            result[f'Frequency_{i+1}'] = result['WinningNumbers'].apply(lambda x: x[i][1])

        # Drop the original WinningNumbers column
        result.drop(columns='WinningNumbers', inplace=True)
        print(result)
        # Export to Excel
        with pd.ExcelWriter(f"Ontario49_Most_Frequent_Numbers.xlsx") as writer:
            result.to_excel(writer, index=False, sheet_name="Frequency by Month")

        return "Ontario49_Most_Frequent_Numbers.xlsx"
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return e


async def scrape_lottario_wining_numbers(db: Session):
    try:
        all_numbers = []
        for num in range(1, 25):
            response = requests.get(f"https://www.lotto-8.com/canada/listltoCALO45.asp?indexpage={num}")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", class_="auto-style1")
            rows = table.find_all("tr")
            print(rows)
            for row in rows[1:]:
                date_cell = row.find_all("td")[0].get_text(strip=True).split("\n")[0].split("(")[0]
                numbers_cell = row.find_all("td")[1].get_text(strip=True).replace("\u00a0", "").split(",")
                bonus_ball_cell = row.find_all("td")[2].get_text(strip=True)
                day = date_cell[:2]   # Extract day
                month = date_cell[3:5]  # Extract month
                year = date_cell[5:]  # Extract year

                formatted_date = f"{day}-{month}-{year}"
                all_numbers.append({
                    "Date": formatted_date,
                    "WinningNumbers": numbers_cell,
                    "BonusBall": bonus_ball_cell,
                })

        df = pd.DataFrame(all_numbers)
        # Step 4: Track occurrences of all numbers (1-99) for each day
        all_numbers_occurred = {str(i): [] for i in range(1, 100)}  # Create a dictionary to hold counts for each number

        # Step 4a: Loop through each row and count occurrences of each number
        for index, row in df.iterrows():
            winning_numbers = row['WinningNumbers']
            for number in range(1, 100):
                # Check if the number is in the winning numbers for this draw
                if str(number) in winning_numbers:
                    all_numbers_occurred[str(number)].append(row['Date'])

        # Step 5: Create a frequency table of occurrences
        number_frequency_by_day = {}
        for number, dates in all_numbers_occurred.items():
            # Count occurrences of the number for each day
            day_count = pd.Series(dates).value_counts().to_dict()
            number_frequency_by_day[number] = day_count

        # Step 6: Find the most frequent number for each day
        most_frequent_number_by_day = {}

        for date in df['Date'].unique():
            max_frequency = 0
            most_frequent_number = None
            for number, day_counts in number_frequency_by_day.items():
                count = day_counts.get(date, 0)
                if count > max_frequency:
                    max_frequency = count
                    most_frequent_number = number
            most_frequent_number_by_day[date] = most_frequent_number

        # Step 7: Add comments to the Excel sheet for the most frequent number of each day
        df['comments'] = df['Date'].apply(lambda x: f"Most frequent number: {most_frequent_number_by_day.get(x, 'N/A')}" if x in most_frequent_number_by_day else "")
        today = datetime.today()
        # Step 8: Save the data with comments to an Excel file
        excel_file = f'lottario_winning_results.xlsx'
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Lotto Results', index=False)
            worksheet = writer.sheets['Lotto Results']

            # Add comments to the Excel cells for the most frequent number of each day
            for row_idx, date in enumerate(df['Date']):
                if df.at[row_idx, 'comments']:
                    worksheet.write_comment(f'F{row_idx+2}', df.at[row_idx, 'comments'])  # Assuming 'comments' in column 'F'

        # Output the result to the console
        print(f"Most frequent numbers have been tracked and saved to '{excel_file}'.")
        return excel_file
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"status": "error", "message": str(e)}, 500
    
async def scrape_lottario_winning_frequency(db: Session):
    try:
        all_numbers = []
        for num in range(1, 25):
            response = requests.get(f"https://www.lotto-8.com/canada/listltoCALO45.asp?indexpage={num}")
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", class_="auto-style1")
            rows = table.find_all("tr")
            print(rows)
            for row in rows[1:]:
                date_cell = row.find_all("td")[0].get_text(strip=True).split("\n")[0].split("(")[0]
                numbers_cell = row.find_all("td")[1].get_text(strip=True).replace("\u00a0", "").split(",")
                bonus_ball_cell = row.find_all("td")[2].get_text(strip=True)
                day = date_cell[:2]   # Extract day
                month = date_cell[3:5]  # Extract month
                year = date_cell[5:]  # Extract year

                formatted_date = f"{day}-{month}-{year}"
                all_numbers.append({
                    "Date": formatted_date,
                    "WinningNumbers": numbers_cell,
                    "BonusBall": bonus_ball_cell,
                })
        df = pd.DataFrame(all_numbers)
        
        df['Date'] = pd.to_datetime(df['Date'])

        # Extract the month and year for grouping
        df['Month'] = df['Date'].dt.to_period('M')

        # Function to find the most frequent numbers
        def top_frequent(numbers_list, top_n=4):
            # Flatten the list of lists
            flat_list = [num for sublist in numbers_list for num in sublist]
            # Count occurrences
            freq_counter = Counter(flat_list)
            # Get the top_n most common numbers
            most_common = freq_counter.most_common(top_n)
            # Pad with (None, 0) if less than top_n numbers
            most_common += [(None, 0)] * (top_n - len(most_common))
            # Return only numbers and their frequencies
            return most_common

        # Group by Month and calculate the top frequent numbers for each month
        result = df.groupby('Month')['WinningNumbers'].apply(lambda x: top_frequent(x, top_n=4)).reset_index()
        # sort values by month
        result =  result.sort_values(by='Month', ascending=False)
        # Split the results into separate columns for each rank
        for i in range(4):  # Adjust range for the desired top_n numbers
            result[f'MostFrequentNumber_{i+1}'] = result['WinningNumbers'].apply(lambda x: x[i][0])
            result[f'Frequency_{i+1}'] = result['WinningNumbers'].apply(lambda x: x[i][1])

        # Drop the original WinningNumbers column
        result.drop(columns='WinningNumbers', inplace=True)
        print(result)
        # Export to Excel
        with pd.ExcelWriter(f"Lottario_Most_Frequent_Numbers.xlsx") as writer:
            result.to_excel(writer, index=False, sheet_name="Frequency by Month")
       
        return "Lottario_Most_Frequent_Numbers.xlsx"
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"status": "error", "message": str(e)}, 500
    