class CreateCollections < ActiveRecord::Migration[7.0]
  def change
    create_table :collections do |t|
      t.string :name, null: false
      t.string :description
      t.string :url
      t.jsonb :inverted_index, default: {}

      t.timestamps
    end
  end
end
