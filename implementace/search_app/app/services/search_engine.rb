# frozen_string_literal: true

# Class for finding and ranking documents based on relevance
class SearchEngine
  attr_reader :inverted_index, :lang, :query, :queried_tokens, :en_postings, :cz_postings, :found_documents

  def initialize(collection, query, lang)
    @inverted_index = collection.inverted_index
    @query = query
    @lang = lang
  end

  def search
    @en_postings = []
    @cz_postings = []
    relevance = { query: Hash.new(0), translation: {} }
    @queried_tokens = Hash.new { |h, k| h[k] = [] }
    tokens = query.split(' ')
    tokens.each do |token|
      res = find_nearest_translations(token)
      next unless res

      nearest_five = res[1..]
      token = res[0]
      @queried_tokens[token] = nearest_five
      next if nearest_five.empty?

      nearest_five.each_with_index do |key, idx|
        inverted_index[opposite_language(lang)][key]&.each do |doc_id|
          relevance[:translation][doc_id] ||= 1.0
          relevance[:translation][doc_id] *= 1.0 / (idx + 1)
        end
      end
      other_postings = Array.wrap(inverted_index[opposite_language(lang)].slice(*nearest_five).values.flatten)
      query_postings = Array.wrap(inverted_index[lang][token])
      query_postings.each do |posting|
        relevance[:query][posting] += 1
      end
      if lang == 'cz'
        @cz_postings += query_postings
        @en_postings += other_postings
      else
        @en_postings += query_postings
        @cz_postings += other_postings
      end
    end
    all_postings = (@cz_postings | @en_postings)
    @all_relevance = all_postings.map do |posting|
      translation_rel = relevance[:translation][posting] || 0
      query_rel = relevance[:query][posting] / tokens.size
      [posting, (translation_rel.to_f + query_rel) / 2]
    end.to_h
    @found_documents = Document.where(id: all_postings).sort_by { |v| -@all_relevance[v.id] }
  end

  def text_in_results?(document, lang)
    send("#{lang}_postings").include? document.id
  end

  def best_token_for_text(document, language)
    doc_tokend = language == 'en' ? document.english_tokens : document.czech_tokens
    query_tokens = tokens_for_language(language)
    query_tokens.each do |token|
      return token if doc_tokend.include? token
    end
    ''
  end

  def tokens_for_language(language)
    language == lang ? queried_tokens.keys : queried_tokens.values.flatten
  end

  def opposite_language(language)
    language == 'en' ? 'cz' : 'en'
  end

  def relevance_for(document)
    @all_relevance[document.id]
  end

  private

  def find_nearest_translations(token)
    res = `python python_search/search.py #{lang} #{token}`
    return if res.empty?

    JSON.parse(res.gsub("'", '"'))
  end
end
