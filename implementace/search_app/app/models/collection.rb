# frozen_string_literal: true

class Collection < ApplicationRecord
  has_many :documents

  def to_s
    name
  end
end
