# frozen_string_literal: true

# Controller for Collection models
class CollectionsController < ApplicationController
  before_action :load_item, only: %i[show generate_index show_index]

  def index
    @collections = Collection.all
  end

  def show; end

  def generate_index
    generator = IndexGenerator.new(@collection)
    if generator.generate
      flash.now[:success] = "Inverted index was successfully created in #{generator.last_executed_time.round(3)} ms"
    else
      flash.now[:warning] = 'There were some troubles during index generation'
    end
    render :show
  end

  def show_index
    @index = @collection.inverted_index
  end

  private

  def load_item
    @collection = Collection.find(params[:id])
  end
end
