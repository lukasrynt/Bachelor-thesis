class CreateDocuments < ActiveRecord::Migration[7.0]
  def change
    create_table :documents do |t|
      t.string :identifier, null: false
      t.string :czech_text
      t.string :english_text
      t.text :czech_tokens, array: true, default: []
      t.text :english_tokens, array: true, default: []
      t.references :collection, foreign_key: true

      t.timestamps
    end
  end
end
