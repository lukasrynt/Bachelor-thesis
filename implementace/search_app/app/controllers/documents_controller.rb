# frozen_string_literal: true

# Controller for Document models
class DocumentsController < ApplicationController
  before_action :load_item, only: %i[show]

  def index
    @pagy, @documents = pagy(load_index_items)
  end

  def show; end

  def search
    @collection = Collection.find_by(id: params[:collection_id])
    @query = params[:query]
    @language = params[:language]
    @engine = SearchEngine.new(@collection, @query, @language)
    @engine.search
    @pagy, @documents = pagy_array(@engine.found_documents)
  end

  private

  def load_item
    @document = Document.find(params[:id])
  end

  def load_index_items
    if params[:collection_id]
      Document.for_collection_id(params[:collection_id])
    else
      Document.all
    end
  end
end
