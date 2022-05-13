# frozen_string_literal: true

class Document < ApplicationRecord
  belongs_to :collection

  scope :for_collection_id, ->(collection_id) { where(collection_id: collection_id) }
end
