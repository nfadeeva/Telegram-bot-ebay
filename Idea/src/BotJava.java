import com.pengrad.telegrambot.TelegramBot;
import com.pengrad.telegrambot.TelegramBotAdapter;
import com.pengrad.telegrambot.request.SendMessage;
import com.pengrad.telegrambot.response.*;
public class BotJava {
    private TelegramBot bot;
    private String chatId;
    public BotJava(String chatId, String botToken){
        this.bot = TelegramBotAdapter.build(botToken);
        this.chatId = chatId;
    }
    public void sendMessage(String text){
        bot.execute(new SendMessage(chatId, text));
    }

}