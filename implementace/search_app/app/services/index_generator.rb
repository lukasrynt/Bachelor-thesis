# frozen_string_literal: true

# Service for generating inverted index for given collection
class IndexGenerator
  attr_reader :collection, :last_executed_time

  # @param collection [Collection]
  def initialize(collection)
    @collection = collection
  end

  def generate
    inverted_index = {}
    measure { inverted_index = create_inverted_index }
    collection.update inverted_index: inverted_index
  end

  private

  def create_inverted_index
    inverted_index = {
      cz: Hash.new { |h, k| h[k] = Set.new },
      en: Hash.new { |h, k| h[k] = Set.new }
    }
    collection.documents.each do |document|
      document.czech_tokens.each do |token|
        inverted_index[:cz][token] << document.id
      end
      document.english_tokens.each do |token|
        inverted_index[:en][token] << document.id
      end
    end
    inverted_index
  end

  def measure(&block)
    @last_executed_time = Benchmark.realtime do
      block.call
    end * 1000
  end
end
