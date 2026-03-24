import matplotlib.pyplot as plt
import numpy as np

def show_chart(all_books, old_prices):
    plt.close('all')

    if not all_books:
        print("No books to display.")
        return False

    titles = [book[0] for book in all_books]
    prices = [float(book[1][1:]) for book in all_books]

    # Color logic
    colors = []
    for title, price_str in all_books:
        price = float(price_str[1:])
        if title in old_prices:
            old_price = float(old_prices[title][1:])
            colors.append('seagreen' if price < old_price else 'crimson')
        else:
            colors.append('#3498db')   # Nice modern blue

    # === Unique Modern Design ===
    fig, ax = plt.subplots(figsize=(14, 8.5))
    fig.patch.set_facecolor('#f4f6f9')
    ax.set_facecolor('#ffffff')

    x = np.arange(len(titles))
    bars = ax.bar(x, prices, color=colors, width=0.68, 
                  edgecolor='white', linewidth=2, alpha=0.95)

    # Value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.18,
                f'£{height:.2f}', 
                ha='center', va='bottom',
                fontsize=11, fontweight='bold', color='#2c3e50')

    # Show price drop arrows with amount
    for i, (title, price_str) in enumerate(all_books):
        if title in old_prices:
            old_p = float(old_prices[title][1:])
            new_p = prices[i]
            if new_p < old_p:
                drop = old_p - new_p
                ax.annotate(f'↓ £{drop:.2f}', 
                            xy=(i, new_p),
                            xytext=(i, new_p + 1.1),
                            ha='center', va='bottom',
                            fontsize=10, color='seagreen', fontweight='bold',
                            arrowprops=dict(arrowstyle='->', color='seagreen', lw=1.2))

    # Styling
    ax.set_xticks(x)
    ax.set_xticklabels(titles, rotation=45, ha='right', fontsize=10.5, fontweight='medium')
    
    ax.set_ylabel("Price (£)", fontsize=14, fontweight='bold', labelpad=12, color='#2c3e50')
    ax.set_title("📚 Book Price Tracker\n(Green = Price Drop • Red = Price Increase)", 
                 fontsize=17, fontweight='bold', pad=30, color='#2c3e50')

    # Clean look
    ax.grid(axis='y', linestyle='--', alpha=0.35, color='#7f8c8e')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#bdc3c7')
    ax.spines['bottom'].set_color('#bdc3c7')

    ax.axhline(y=0, color='#ecf0f1', linewidth=1.5)

    plt.tight_layout()
    plt.show()
    return True