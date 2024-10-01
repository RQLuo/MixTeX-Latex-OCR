import re
import random
import string
from tqdm import tqdm
import jieba
import os

# Function to remove non-English characters from a text file
# Input:
#   input_file_path (str): Path to the input text file
#   output_file_path (str): Path to save the cleaned text file
# Output:
#   None (writes the cleaned content to output_file_path)
def remove_non_english_characters(input_file_path, output_file_path):
    english_regex = re.compile(r'[^a-zA-Z0-9\s.,?!\'"()]+')
    with open(input_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    cleaned_content = english_regex.sub('', content)
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_content)

# Function to extract LaTeX formulas from a .tex file
# Input:
#   tex_file_path (str): Path to the LaTeX (.tex) file
# Output:
#   formula_list (list): List of extracted LaTeX formulas
def extract_latex_formulas(tex_file_path):
    with open(tex_file_path, 'r', encoding='utf-8') as f:
        tex_content = f.read()
    pattern = r'\\\[(.+?)\\\]|\\begin{align\*}(.+?)\\end{align\*}'
    formulas = re.findall(pattern, tex_content)
    formula_list = [re.sub(r'\\eqref\{(.*?)\}', r'', group) for tuples in formulas for group in tuples if group]
    return formula_list

# Function to process text by inserting LaTeX formulas randomly
# Input:
#   input_file (str): Path to the input text file
#   output_file (str): Path to save the processed text file
#   formulas (list): List of LaTeX formulas to insert
# Output:
#   None (writes the processed content to output_file)
def process_text(input_file, output_file, formulas):
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    text = text.replace('\n', '')
    sentences = re.split(r'[.,]', text)
    output = ''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for sentence in sentences:
            for char in sentence:
                output += char
                if random.random() < 0.02:
                    formula = random.sample(formulas, 1)[0]
                    if len(formula) < 50:
                        try:
                            output += ' \\(' + re.sub(r'\\tag\{.*?\}', '', formula) + '\\) '
                        except:
                            print(formula)
            if 30 < len(output) < 300:
                f.write(output + '.\n')
                output = ''
            if len(output) > 300:
                output = ''

# Function to remove unwanted symbols from text
# Input:
#   text (str): The input text string
# Output:
#   cleaned_text (str): The text after removing unwanted symbols
def remove_symbols(text):
    pattern = re.compile(r'[^\u4e00-\u9fa5a-zA-Z，。！？、： ；“”‘’\'\"\(\)\[\]\{\}\<\>\.\,\?\!\:\;\-]')
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text

# Function to format words with LaTeX commands and randomly insert formulas and numbers
# Input:
#   words (list): List of words to format
#   formulas (list): List of LaTeX formulas to insert
#   lines (list): List of lines from the original text for random insertion
# Output:
#   output (str): The formatted LaTeX string
def format_text_with_latex(words, formulas, lines):
    output = ''
    count = 0
    for char in tqdm(words):
        count += 1
        if len(char) >= 2 and random.random() < 0.01:
            if random.random() < 0.5:
                output += ' \\textbf{' + char + '} '
            else:
                output += ' \\textit{' + char + '} '
        else:
            output += char
        if count % 100 == 0:
            output += '\n \\newpage \n'
        if random.random() < 0.5:
            if random.random() < 0.03:
                formula = random.sample(formulas, 1)[0]
                if random.random() < 0.03:
                    formula += '\\tag{' + str(random.randint(0, 20)) + '.' + str(random.randint(0, 20)) + '}'
                if len(formula) > 30:
                    output += '\n \\begin{align*} \n' + formula + '\n \\end{align*} \n'
            else:
                formula = random.sample(formulas, 1)[0]
                if len(formula) < 30:
                    output += ' \\( ' + re.sub(r'\\tag\{.*?\}', '', formula) + ' \\) '
        elif random.random() < 0.007:
            output += ' \\(' + str(random.randint(-1000, 1000)) + '\\) '
        elif random.random() < 0.007:
            rand_num = random.randint(-99, 99) / random.randint(1, 99)
            rand_float = str(round(rand_num, random.randint(1, 4)))
            output += ' \\(' + rand_float + '\\) '
        elif random.random() < 0.007:
            rand_str = ''.join(random.choices(string.ascii_letters, k=random.randint(1, 3)))
            output += ' \\(' + rand_str + '\\) '
        if random.random() < 0.001:
            output += ' \\([' + str(random.randint(1, 100)) + ']\\) '
        if random.random() < 0.0005:
            char = random.sample(lines, 1)[0].replace('\n', '')
            if random.random() < 0.5:
                output += ' \\textbf{' + char + '} '
            else:
                output += ' \\textit{' + char + '} '
    return output

# Function to write LaTeX formatted strings into separate .tex files
# Input:
#   strings (str): The LaTeX formatted string to write
#   group_size (int, optional): Number of characters per file.
#   folder_name (str, optional): Name of the folder to save .tex files.
# Output:
#   None (writes multiple .tex files into the specified folder)
def write_strings_to_files(strings, group_size, folder_name):
    os.makedirs(folder_name, exist_ok=True)
    num_files = (len(strings) + group_size - 1) // group_size
    
    for i in range(num_files):
        file_name = f"{folder_name}/{i + 1}.tex"
        start_index = i * group_size
        end_index = start_index + group_size
        current_group = strings[start_index:end_index]
        width = random.randint(12, 15)
        margin = random.randint(3, 4)
        line = random.randint(4, 20) / 10
        bg = f'\\documentclass{{ctexart}}\n\\usepackage[paperwidth={width}in, paperheight=36in, margin={margin}in]{{geometry}}\n'
        bg += '\\usepackage{amssymb}\n\\usepackage{amsmath}\n\\usepackage{stmaryrd}\n\\usepackage{color}\n'
        bg += '\\nonstopmode\n\\pagestyle{empty}\n\\renewcommand{\\baselinestretch}{' + str(line) + '}\n\n\\begin{document}\n \\newpage'
        ed = '\\end{document}'
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(bg)
            file.write(''.join(current_group))
            file.write(ed)

# Main function to connect all steps
# Input:
#   input_text_file (str): Path to the input text file
#   input_tex_file (str): Path to the input LaTeX (.tex) file containing formulas
#   output_folder (str): Folder name to save the output .tex files
# Output:
#   None (executes the entire processing pipeline and writes output files)
def main(input_text_file, input_tex_file, output_folder):
    # Step 1: Clean the input text file by removing non-English characters
    cleaned_text_file = 'en_only.txt'
    remove_non_english_characters(input_text_file, cleaned_text_file)

    # Step 2: Extract LaTeX formulas from the input LaTeX file
    formulas = extract_latex_formulas(input_tex_file)

    # Step 3: Process the cleaned text and insert LaTeX formulas randomly
    processed_text_file = 'en_line.txt'
    process_text(cleaned_text_file, processed_text_file, formulas)

    # Step 4: Read in the processed text and further format it with LaTeX commands
    with open(processed_text_file, 'r', encoding='utf-8') as f:
        txt_content = f.read()
    with open(cleaned_text_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    txt_content = remove_symbols(txt_content)
    words = jieba.lcut(txt_content)
    latex_content = format_text_with_latex(words, formulas, lines)

    # Step 5: Write the formatted LaTeX strings into .tex files in the specified folder
    write_strings_to_files(latex_content, folder_name=output_folder)

# Example usage
if __name__ == "__main__":
    main('endata1.txt', 'formular.tex', 'en')
