# frozen_string_literal: true

require 'csv'
require 'json'

# UFAL abstracts
path = '../word2vec/corpus/ufal/ufal_with_tokens.csv'
ufal = Collection.find_or_create_by(name: 'UFAL')
ufal.description = "This is a document-aligned parallel corpus of English and Czech abstracts of scientific papers published by authors from the Institute of Formal and Applied Linguistics, Charles University in Prague, as reported in the institute's system Biblio. For each publication, the authors are obliged to provide both the original abstract in Czech or English, and its translation into English or Czech, respectively. No filtering was performed, except for removing entries missing the Czech or English abstract, and replacing newline and tabulator characters by spaces."
ufal.url = 'https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-1731'
ufal.save

data = CSV.read(path, headers: true)
data.each do |row|
  document = Document.find_or_create_by(identifier: "UFAL-#{row['ID']}")
  document.assign_attributes(collection: ufal, english_text: row['EN'], czech_text: row['CZ'],
                             english_tokens: JSON.parse(row['EN_tokens'].gsub('\'', '"')).uniq,
                             czech_tokens: JSON.parse(row['CZ_tokens'].gsub('\'', '"')).uniq)
  document.save
end

def read_file(file_path)
  f = File.open(file_path)
  f.read
end

# EurLex dataset
path = '../word2vec/corpus/eurlex/'
eurlex = Collection.find_or_create_by(name: 'EurLex')
eurlex.description = 'Created corpus of data from EUR-Lex server containing legal contracts.'
eurlex.url = 'https://eur-lex.europa.eu/homepage.html?locale=cs'
eurlex.save
Dir.each_child(path) do |folder_name|
  curr_path = path + folder_name
  next unless File.directory?(curr_path)

  document = Document.find_or_create_by(identifier: folder_name)
  document.assign_attributes(collection: eurlex,
                             english_text: read_file("#{curr_path}/en.txt"),
                             czech_text: read_file("#{curr_path}/cz.txt"),
                             english_tokens: JSON.parse(read_file("#{curr_path}/en_tokens.json")).flatten!.uniq,
                             czech_tokens: JSON.parse(read_file("#{curr_path}/cz_tokens.json")).flatten!.uniq)
  document.save
end
