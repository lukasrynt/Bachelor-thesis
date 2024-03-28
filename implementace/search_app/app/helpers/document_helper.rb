# frozen_string_literal: true

module DocumentHelper
  def document_index_title
    if params[:collection_id]
      "Documents for corpus #{Collection.find(params[:collection_id])}"
    else
      'All documents'
    end
  end

  def language_title(lang)
    case lang
    when 'cz'
      'Czech'
    when 'en'
      'English'
    else
      'Unknown'
    end
  end

  def highlight_and_truncate(document, lang, engine = nil, length: 100)
    text = lang == 'en' ? document.english_text : document.czech_text
    return truncate text, length: length, separator: ' ' if !engine || !engine.text_in_results?(document, lang)

    token = engine.best_token_for_text(document, lang)
    index = text =~ Regexp.new(token, Regexp::IGNORECASE)
    text = if !index || index.zero?
             "#{text[..length]}..."
           else
             "...#{text[index..(index + length)]}..."
           end
    highlight(text, engine.tokens_for_language(lang))
  end
end
